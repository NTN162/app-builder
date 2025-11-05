"""
Nesting Engine - Thuật toán sắp xếp và tối ưu hóa layout
Implementation inspired by SVGNest/Deepnest algorithms
"""

from shapely.geometry import Polygon, Point, box
from shapely.affinity import translate, rotate, scale
from shapely.ops import unary_union
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class NestingPart:
    """Đại diện cho một part cần nest"""
    id: str
    polygon: Polygon
    original_path: str
    layer: str
    rotation_allowed: bool = True
    rotation_step: float = 90  # degrees
    quantity: int = 1
    metadata: Dict = None


@dataclass
class PlacedPart:
    """Part đã được đặt vào sheet"""
    part: NestingPart
    x: float
    y: float
    rotation: float
    polygon: Polygon  # Transformed polygon


class NestingEngine:
    """
    Engine thực hiện thuật toán nesting
    Sử dụng Bottom-Left (BL) heuristic với rotation
    """

    def __init__(self,
                 sheet_width: float,
                 sheet_height: float,
                 spacing: float = 5.0,
                 rotation_enabled: bool = True):
        """
        Initialize nesting engine

        Args:
            sheet_width: Chiều rộng sheet/material
            sheet_height: Chiều cao sheet/material
            spacing: Khoảng cách tối thiểu giữa các parts
            rotation_enabled: Cho phép xoay parts
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.spacing = spacing
        self.rotation_enabled = rotation_enabled
        self.sheet = box(0, 0, sheet_width, sheet_height)
        self.placed_parts: List[PlacedPart] = []

    def svg_path_to_polygon(self, path_string: str) -> Optional[Polygon]:
        """
        Convert SVG path string sang Shapely Polygon

        Args:
            path_string: SVG path string

        Returns:
            Shapely Polygon hoặc None nếu không parse được
        """
        try:
            from svgpathtools import parse_path

            path = parse_path(path_string)
            points = []

            # Sample points dọc theo path
            num_samples = max(100, int(path.length() / 2))
            for i in range(num_samples):
                t = i / (num_samples - 1)
                point = path.point(t)
                points.append((point.real, point.imag))

            if len(points) >= 3:
                polygon = Polygon(points)
                # Simplify để giảm số điểm
                polygon = polygon.simplify(tolerance=0.5, preserve_topology=True)
                return polygon
            return None

        except Exception as e:
            print(f"Error converting path to polygon: {e}")
            return None

    def apply_spacing(self, polygon: Polygon) -> Polygon:
        """
        Thêm spacing buffer vào polygon

        Args:
            polygon: Original polygon

        Returns:
            Buffered polygon
        """
        if self.spacing > 0:
            return polygon.buffer(self.spacing / 2, join_style=2)
        return polygon

    def get_rotation_angles(self, part: NestingPart) -> List[float]:
        """
        Lấy danh sách các góc xoay cần test

        Args:
            part: Nesting part

        Returns:
            List of angles in degrees
        """
        if not self.rotation_enabled or not part.rotation_allowed:
            return [0]

        angles = []
        step = part.rotation_step
        for angle in range(0, 360, int(step)):
            angles.append(angle)

        return angles

    def find_bottom_left_position(self,
                                  part_polygon: Polygon,
                                  existing_parts: List[PlacedPart]) -> Optional[Tuple[float, float]]:
        """
        Tìm vị trí Bottom-Left hợp lệ cho part

        Args:
            part_polygon: Polygon của part cần đặt
            existing_parts: Các parts đã được đặt

        Returns:
            (x, y) position hoặc None nếu không tìm thấy
        """
        # Bắt đầu từ góc bottom-left
        min_x, min_y, max_x, max_y = part_polygon.bounds
        part_width = max_x - min_x
        part_height = max_y - min_y

        # Thử các vị trí theo grid
        step = max(5, self.spacing)
        tested_positions = []

        # Start positions: corners và edges của existing parts
        test_x_positions = [0]
        test_y_positions = [0]

        for placed in existing_parts:
            px, py, pw, ph = placed.polygon.bounds
            test_x_positions.extend([px, px + pw])
            test_y_positions.extend([py, py + ph])

        # Sort positions
        test_x_positions = sorted(set(test_x_positions))
        test_y_positions = sorted(set(test_y_positions))

        # Thử từng vị trí, ưu tiên bottom-left
        for y in test_y_positions:
            for x in test_x_positions:
                # Translate part đến vị trí test
                offset_x = x - min_x
                offset_y = y - min_y

                test_polygon = translate(part_polygon, xoff=offset_x, yoff=offset_y)

                # Kiểm tra nếu trong sheet
                if not self.sheet.contains(test_polygon):
                    continue

                # Kiểm tra overlap với existing parts
                has_overlap = False
                for placed in existing_parts:
                    if test_polygon.intersects(placed.polygon):
                        has_overlap = True
                        break

                if not has_overlap:
                    return (offset_x, offset_y)

        return None

    def nest_part(self, part: NestingPart) -> bool:
        """
        Thử nest một part vào sheet

        Args:
            part: Part cần nest

        Returns:
            True nếu nest thành công
        """
        # Thử các góc xoay khác nhau
        angles = self.get_rotation_angles(part)
        best_position = None
        best_angle = 0
        best_polygon = None

        for angle in angles:
            # Rotate polygon
            rotated = rotate(part.polygon, angle, origin='centroid')

            # Apply spacing
            buffered = self.apply_spacing(rotated)

            # Tìm vị trí
            position = self.find_bottom_left_position(buffered, self.placed_parts)

            if position:
                # Tìm được vị trí hợp lệ
                best_position = position
                best_angle = angle
                best_polygon = translate(buffered, xoff=position[0], yoff=position[1])
                break  # Sử dụng vị trí đầu tiên tìm được

        if best_position:
            # Đặt part vào sheet
            placed = PlacedPart(
                part=part,
                x=best_position[0],
                y=best_position[1],
                rotation=best_angle,
                polygon=best_polygon
            )
            self.placed_parts.append(placed)
            return True

        return False

    def nest_parts(self, parts: List[NestingPart]) -> Dict:
        """
        Nest tất cả parts vào sheet

        Args:
            parts: List of parts cần nest

        Returns:
            Dictionary với kết quả nesting
        """
        # Reset
        self.placed_parts = []

        # Sort parts theo diện tích (lớn nhất trước)
        sorted_parts = sorted(parts, key=lambda p: p.polygon.area, reverse=True)

        # Expand parts theo quantity
        expanded_parts = []
        for part in sorted_parts:
            for i in range(part.quantity):
                # Clone part
                expanded_parts.append(part)

        # Nest từng part
        nested_count = 0
        failed_parts = []

        for part in expanded_parts:
            if self.nest_part(part):
                nested_count += 1
            else:
                failed_parts.append(part)

        # Tính utilization
        total_area = sum(p.part.polygon.area for p in self.placed_parts)
        sheet_area = self.sheet_width * self.sheet_height
        utilization = (total_area / sheet_area) * 100 if sheet_area > 0 else 0

        return {
            'success': len(failed_parts) == 0,
            'placed_parts': self.placed_parts,
            'failed_parts': failed_parts,
            'nested_count': nested_count,
            'total_count': len(expanded_parts),
            'utilization': utilization,
            'sheet_width': self.sheet_width,
            'sheet_height': self.sheet_height
        }

    def get_placement_svg_transforms(self) -> List[Dict]:
        """
        Lấy các transform parameters cho SVG export

        Returns:
            List of transform dictionaries
        """
        transforms = []

        for placed in self.placed_parts:
            transform = {
                'id': placed.part.id,
                'translate': (placed.x, placed.y),
                'rotate': placed.rotation,
                'original_path': placed.part.original_path,
                'layer': placed.part.layer,
                'metadata': placed.part.metadata
            }
            transforms.append(transform)

        return transforms

    def calculate_bounding_box(self) -> Dict:
        """
        Tính bounding box của tất cả placed parts

        Returns:
            Dictionary với x, y, width, height
        """
        if not self.placed_parts:
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}

        all_bounds = [p.polygon.bounds for p in self.placed_parts]
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)

        return {
            'x': min_x,
            'y': min_y,
            'width': max_x - min_x,
            'height': max_y - min_y
        }
