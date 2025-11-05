"""
PDF Extractor - Trích xuất hình dạng khuôn bế từ PDF
Extracts die-cut shapes from PDF files with 'cut' stroke color
"""

import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
import re
from pathlib import Path


class PDFShapeExtractor:
    """
    Trích xuất các hình dạng có stroke màu 'cut' từ file PDF
    """

    def __init__(self, pdf_path: str):
        """
        Initialize PDF extractor

        Args:
            pdf_path: Đường dẫn đến file PDF
        """
        self.pdf_path = Path(pdf_path)
        self.doc = None
        self.shapes = []

    def open(self):
        """Mở file PDF"""
        try:
            self.doc = fitz.open(self.pdf_path)
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False

    def close(self):
        """Đóng file PDF"""
        if self.doc:
            self.doc.close()

    def extract_paths_from_page(self, page_num: int = 0) -> List[Dict]:
        """
        Trích xuất các đường path từ một trang

        Args:
            page_num: Số thứ tự trang (bắt đầu từ 0)

        Returns:
            List of path dictionaries với thông tin về paths
        """
        if not self.doc:
            self.open()

        page = self.doc[page_num]
        paths = []

        # Lấy drawing commands từ page
        drawings = page.get_drawings()

        for drawing in drawings:
            # Kiểm tra stroke color
            stroke_color = drawing.get('color')
            stroke_name = drawing.get('stroke_name', '')

            # Tìm các path có stroke màu 'cut' hoặc tên chứa 'cut'
            if self._is_cut_stroke(stroke_color, stroke_name):
                path_data = {
                    'type': drawing.get('type'),
                    'rect': drawing.get('rect'),
                    'items': drawing.get('items', []),
                    'stroke_color': stroke_color,
                    'stroke_width': drawing.get('width', 1.0),
                    'fill': drawing.get('fill'),
                    'layer': self._extract_layer_name(drawing)
                }
                paths.append(path_data)

        return paths

    def _is_cut_stroke(self, color: Optional[Tuple], name: str) -> bool:
        """
        Kiểm tra xem stroke có phải là màu 'cut' không

        Args:
            color: RGB color tuple
            name: Tên màu hoặc layer

        Returns:
            True nếu là cut stroke
        """
        if name and 'cut' in name.lower():
            return True

        # Kiểm tra các màu thường dùng cho cut (magenta, cyan, red)
        if color:
            # Magenta (1, 0, 1) thường dùng cho cut
            if len(color) >= 3 and color[0] > 0.9 and color[2] > 0.9 and color[1] < 0.1:
                return True
            # Cyan (0, 1, 1) cũng thường dùng
            if len(color) >= 3 and color[1] > 0.9 and color[2] > 0.9 and color[0] < 0.1:
                return True

        return False

    def _extract_layer_name(self, drawing: Dict) -> str:
        """
        Trích xuất tên layer từ drawing

        Args:
            drawing: Dictionary chứa thông tin drawing

        Returns:
            Tên layer
        """
        # Thử lấy từ properties khác nhau
        layer = drawing.get('layer', '')
        if not layer:
            layer = drawing.get('name', '')
        if not layer:
            layer = 'default'

        return layer

    def convert_to_svg_path(self, path_data: Dict) -> str:
        """
        Convert PDF path sang SVG path string

        Args:
            path_data: Dictionary chứa thông tin path

        Returns:
            SVG path string (d attribute)
        """
        svg_commands = []
        items = path_data.get('items', [])

        for item in items:
            if item[0] == 'l':  # Line
                p1, p2 = item[1], item[2]
                if not svg_commands:
                    svg_commands.append(f"M {p1.x:.2f} {p1.y:.2f}")
                svg_commands.append(f"L {p2.x:.2f} {p2.y:.2f}")

            elif item[0] == 'c':  # Curve (Bezier)
                p1, p2, p3, p4 = item[1], item[2], item[3], item[4]
                if not svg_commands:
                    svg_commands.append(f"M {p1.x:.2f} {p1.y:.2f}")
                svg_commands.append(
                    f"C {p2.x:.2f} {p2.y:.2f}, {p3.x:.2f} {p3.y:.2f}, {p4.x:.2f} {p4.y:.2f}"
                )

            elif item[0] == 're':  # Rectangle
                rect = item[1]
                x, y, w, h = rect.x0, rect.y0, rect.width, rect.height
                svg_commands.append(
                    f"M {x:.2f} {y:.2f} L {x+w:.2f} {y:.2f} L {x+w:.2f} {y+h:.2f} L {x:.2f} {y+h:.2f} Z"
                )

        return " ".join(svg_commands)

    def extract_all_cut_shapes(self) -> List[Dict]:
        """
        Trích xuất tất cả các hình dạng cut từ toàn bộ PDF

        Returns:
            List of shape dictionaries
        """
        if not self.doc:
            self.open()

        all_shapes = []

        for page_num in range(len(self.doc)):
            page_shapes = self.extract_paths_from_page(page_num)
            for shape in page_shapes:
                shape['page'] = page_num
                shape['svg_path'] = self.convert_to_svg_path(shape)
                all_shapes.append(shape)

        self.shapes = all_shapes
        return all_shapes

    def get_page_dimensions(self, page_num: int = 0) -> Tuple[float, float]:
        """
        Lấy kích thước của trang

        Args:
            page_num: Số thứ tự trang

        Returns:
            (width, height) tuple
        """
        if not self.doc:
            self.open()

        page = self.doc[page_num]
        rect = page.rect
        return (rect.width, rect.height)

    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
