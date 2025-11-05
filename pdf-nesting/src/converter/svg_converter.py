"""
SVG Converter - Chuyển đổi giữa PDF paths và SVG
Converts between PDF paths and SVG format for nesting
"""

import svgwrite
from svgpathtools import parse_path, Path, Line, CubicBezier, QuadraticBezier
from typing import List, Dict, Tuple
from pathlib import Path as FilePath
import xml.etree.ElementTree as ET


class SVGConverter:
    """
    Chuyển đổi shapes từ PDF sang SVG và ngược lại
    """

    def __init__(self, width: float = 1000, height: float = 1000):
        """
        Initialize SVG converter

        Args:
            width: Chiều rộng canvas SVG
            height: Chiều cao canvas SVG
        """
        self.width = width
        self.height = height
        self.dwg = None

    def create_svg_from_shapes(self, shapes: List[Dict], output_path: str) -> str:
        """
        Tạo file SVG từ danh sách shapes

        Args:
            shapes: List of shape dictionaries từ PDF extractor
            output_path: Đường dẫn output SVG file

        Returns:
            Path to created SVG file
        """
        # Tạo SVG drawing
        self.dwg = svgwrite.Drawing(
            output_path,
            size=(f'{self.width}px', f'{self.height}px'),
            viewBox=f'0 0 {self.width} {self.height}'
        )

        # Tạo các layer groups
        layers = {}

        for idx, shape in enumerate(shapes):
            layer_name = shape.get('layer', 'default')

            # Tạo layer group nếu chưa có
            if layer_name not in layers:
                layers[layer_name] = self.dwg.g(
                    id=f'layer_{layer_name}',
                    class_='cut-layer'
                )
                self.dwg.add(layers[layer_name])

            # Thêm path vào layer
            path = self.dwg.path(
                d=shape['svg_path'],
                id=f'shape_{idx}',
                class_='cut-path',
                stroke='magenta',
                stroke_width=shape.get('stroke_width', 1),
                fill='none'
            )

            # Thêm metadata
            path.attribs['data-original-page'] = str(shape.get('page', 0))
            if 'layer' in shape:
                path.attribs['data-layer'] = shape['layer']

            layers[layer_name].add(path)

        # Save SVG file
        self.dwg.save()
        return output_path

    def parse_svg_shapes(self, svg_path: str) -> List[Dict]:
        """
        Parse SVG file và extract shapes

        Args:
            svg_path: Đường dẫn đến SVG file

        Returns:
            List of parsed shapes
        """
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # Handle SVG namespaces
        namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        shapes = []

        # Tìm tất cả path elements
        for path_elem in root.findall('.//svg:path', namespaces):
            path_data = path_elem.get('d')
            if not path_data:
                continue

            shape = {
                'svg_path': path_data,
                'id': path_elem.get('id', ''),
                'class': path_elem.get('class', ''),
                'layer': path_elem.get('data-layer', 'default'),
                'stroke': path_elem.get('stroke', 'magenta'),
                'stroke_width': float(path_elem.get('stroke-width', 1)),
                'transform': path_elem.get('transform', ''),
                'original_page': path_elem.get('data-original-page', '0')
            }

            # Parse path để lấy bounding box
            try:
                parsed_path = parse_path(path_data)
                bbox = parsed_path.bbox()
                shape['bbox'] = {
                    'x': bbox[0],
                    'y': bbox[1],
                    'width': bbox[2] - bbox[0],
                    'height': bbox[3] - bbox[1]
                }
            except Exception as e:
                print(f"Warning: Could not parse path {shape['id']}: {e}")
                shape['bbox'] = None

            shapes.append(shape)

        return shapes

    def get_path_bounds(self, path_string: str) -> Dict:
        """
        Lấy bounding box của một SVG path

        Args:
            path_string: SVG path string

        Returns:
            Dictionary với x, y, width, height
        """
        try:
            path = parse_path(path_string)
            bbox = path.bbox()
            return {
                'x': bbox[0],
                'y': bbox[1],
                'width': bbox[2] - bbox[0],
                'height': bbox[3] - bbox[1]
            }
        except:
            return None

    def simplify_path(self, path_string: str, tolerance: float = 1.0) -> str:
        """
        Đơn giản hóa path (giảm số điểm) trong khi giữ hình dạng

        Args:
            path_string: Original SVG path
            tolerance: Tolerance cho simplification (pixels)

        Returns:
            Simplified path string
        """
        try:
            path = parse_path(path_string)
            # TODO: Implement proper simplification algorithm
            # For now, return original
            return path_string
        except:
            return path_string

    def transform_path(self, path_string: str,
                      translate: Tuple[float, float] = (0, 0),
                      rotate: float = 0,
                      scale: float = 1.0) -> str:
        """
        Apply transformations đến path

        Args:
            path_string: Original SVG path
            translate: (x, y) translation
            rotate: Rotation angle in degrees
            scale: Scale factor

        Returns:
            Transformed path string
        """
        try:
            path = parse_path(path_string)

            # Apply transformations
            if scale != 1.0:
                path = path.scaled(scale)

            if rotate != 0:
                from math import radians
                path = path.rotated(radians(rotate))

            if translate != (0, 0):
                path = path.translated(complex(translate[0], translate[1]))

            return path.d()
        except Exception as e:
            print(f"Error transforming path: {e}")
            return path_string

    def merge_paths(self, path_strings: List[str]) -> str:
        """
        Merge nhiều paths thành một path

        Args:
            path_strings: List of SVG path strings

        Returns:
            Merged path string
        """
        merged_commands = []

        for path_str in path_strings:
            if path_str:
                merged_commands.append(path_str)

        return " ".join(merged_commands)
