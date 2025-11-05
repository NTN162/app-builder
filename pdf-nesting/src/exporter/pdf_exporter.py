"""
PDF/AI Exporter - Export nested result ra PDF hoặc AI format
Exports nested layouts to PDF/AI with layer support
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm, inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing, Path, Group
import svgwrite
from typing import List, Dict, Tuple
from pathlib import Path as FilePath
import xml.etree.ElementTree as ET


class PDFExporter:
    """
    Export nested layout sang PDF/AI với layer support
    """

    def __init__(self,
                 page_width: float,
                 page_height: float,
                 units: str = 'mm'):
        """
        Initialize PDF exporter

        Args:
            page_width: Chiều rộng trang
            page_height: Chiều cao trang
            units: Đơn vị ('mm', 'inch', 'pt')
        """
        self.page_width = page_width
        self.page_height = page_height
        self.units = units
        self._setup_units()

    def _setup_units(self):
        """Setup unit conversion"""
        if self.units == 'mm':
            self.unit = mm
        elif self.units == 'inch':
            self.unit = inch
        else:
            self.unit = 1  # points

    def export_to_pdf(self,
                      placed_parts: List,
                      output_path: str,
                      layer_mapping: Dict[str, Dict] = None) -> str:
        """
        Export nested result ra PDF file

        Args:
            placed_parts: List of PlacedPart từ nesting engine
            output_path: Đường dẫn output PDF
            layer_mapping: Mapping tên layer -> properties (color, stroke, etc.)

        Returns:
            Path to created PDF file
        """
        c = canvas.Canvas(output_path,
                         pagesize=(self.page_width * self.unit,
                                  self.page_height * self.unit))

        # Default layer mapping
        if layer_mapping is None:
            layer_mapping = {
                'cut': {'stroke': 'magenta', 'stroke_width': 0.1},
                'score': {'stroke': 'cyan', 'stroke_width': 0.1},
                'default': {'stroke': 'black', 'stroke_width': 0.5}
            }

        # Group parts by layer
        layers = {}
        for placed in placed_parts:
            layer = placed.part.layer
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(placed)

        # Draw từng layer
        for layer_name, parts in layers.items():
            layer_props = layer_mapping.get(layer_name,
                                           layer_mapping.get('default', {}))

            # Set stroke color
            stroke_color = layer_props.get('stroke', 'magenta')
            self._set_stroke_color(c, stroke_color)

            stroke_width = layer_props.get('stroke_width', 0.1) * self.unit
            c.setLineWidth(stroke_width)

            # Draw parts in layer
            for placed in parts:
                self._draw_polygon_on_canvas(c, placed)

        # Save PDF
        c.save()
        return output_path

    def _set_stroke_color(self, c, color_name: str):
        """Set stroke color từ tên màu"""
        colors = {
            'magenta': (1, 0, 1),
            'cyan': (0, 1, 1),
            'red': (1, 0, 0),
            'black': (0, 0, 0),
            'blue': (0, 0, 1),
            'green': (0, 1, 0)
        }

        rgb = colors.get(color_name.lower(), (0, 0, 0))
        c.setStrokeColorRGB(*rgb)

    def _draw_polygon_on_canvas(self, c, placed):
        """Draw một polygon lên PDF canvas"""
        polygon = placed.polygon

        # Get exterior coordinates
        coords = list(polygon.exterior.coords)

        if len(coords) < 2:
            return

        # Start path
        path = c.beginPath()

        # Move to first point
        x0, y0 = coords[0]
        path.moveTo(x0 * self.unit, y0 * self.unit)

        # Draw lines
        for x, y in coords[1:]:
            path.lineTo(x * self.unit, y * self.unit)

        # Close path
        path.close()

        # Draw
        c.drawPath(path, stroke=1, fill=0)

    def export_to_svg_with_layers(self,
                                  placed_parts: List,
                                  output_path: str,
                                  layer_mapping: Dict[str, Dict] = None) -> str:
        """
        Export nested result ra SVG với proper layers

        Args:
            placed_parts: List of PlacedPart
            output_path: Output SVG path
            layer_mapping: Layer properties mapping

        Returns:
            Path to created SVG file
        """
        dwg = svgwrite.Drawing(
            output_path,
            size=(f'{self.page_width}{self.units}',
                  f'{self.page_height}{self.units}'),
            viewBox=f'0 0 {self.page_width} {self.page_height}'
        )

        # Default layer mapping
        if layer_mapping is None:
            layer_mapping = {
                'cut': {'stroke': 'magenta', 'stroke_width': 0.1},
                'score': {'stroke': 'cyan', 'stroke_width': 0.1},
                'default': {'stroke': 'black', 'stroke_width': 0.5}
            }

        # Group parts by layer
        layers = {}
        for placed in placed_parts:
            layer = placed.part.layer
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(placed)

        # Create layer groups
        for layer_name, parts in layers.items():
            layer_props = layer_mapping.get(layer_name,
                                           layer_mapping.get('default', {}))

            # Create group cho layer
            layer_group = dwg.g(
                id=f'layer_{layer_name}',
                class_='cut-layer',
                stroke=layer_props.get('stroke', 'magenta'),
                stroke_width=layer_props.get('stroke_width', 0.1),
                fill='none'
            )

            # Add parts to layer
            for idx, placed in enumerate(parts):
                # Build transform string
                transform_parts = []

                if placed.x != 0 or placed.y != 0:
                    transform_parts.append(f'translate({placed.x},{placed.y})')

                if placed.rotation != 0:
                    # Get centroid for rotation
                    centroid = placed.part.polygon.centroid
                    transform_parts.append(
                        f'rotate({placed.rotation},{centroid.x},{centroid.y})'
                    )

                transform_str = ' '.join(transform_parts) if transform_parts else None

                # Add path
                path = dwg.path(
                    d=placed.part.original_path,
                    id=f'{layer_name}_part_{idx}',
                    class_='nested-part',
                    transform=transform_str
                )

                # Add metadata
                if placed.part.metadata:
                    for key, value in placed.part.metadata.items():
                        path.attribs[f'data-{key}'] = str(value)

                layer_group.add(path)

            dwg.add(layer_group)

        # Save SVG
        dwg.save()
        return output_path

    def export_to_illustrator_ai(self,
                                 placed_parts: List,
                                 output_path: str,
                                 layer_mapping: Dict[str, Dict] = None) -> str:
        """
        Export ra Adobe Illustrator AI format
        AI format về cơ bản là PDF với metadata đặc biệt

        Args:
            placed_parts: List of PlacedPart
            output_path: Output .ai file path
            layer_mapping: Layer properties

        Returns:
            Path to created AI file
        """
        # AI format is essentially PDF with special metadata
        # Export as PDF first
        pdf_path = output_path.replace('.ai', '.pdf')
        self.export_to_pdf(placed_parts, pdf_path, layer_mapping)

        # For full AI support, would need to add Illustrator-specific metadata
        # This is a simplified version
        # Rename to .ai
        import shutil
        shutil.copy(pdf_path, output_path)

        return output_path


class LayerMapper:
    """
    Quản lý mapping giữa layers để tương thích với IMP/AE
    """

    def __init__(self):
        self.layer_map = {}

    def add_layer_mapping(self,
                         layer_name: str,
                         properties: Dict):
        """
        Thêm mapping cho một layer

        Args:
            layer_name: Tên layer
            properties: Dict chứa properties (color, stroke, name, etc.)
        """
        self.layer_map[layer_name] = properties

    def get_layer_properties(self, layer_name: str) -> Dict:
        """Get properties của một layer"""
        return self.layer_map.get(layer_name, {})

    def export_layer_mapping(self, output_path: str):
        """
        Export layer mapping ra JSON file

        Args:
            output_path: Path to JSON file
        """
        import json
        with open(output_path, 'w') as f:
            json.dump(self.layer_map, f, indent=2)

    def import_layer_mapping(self, json_path: str):
        """
        Import layer mapping từ JSON file

        Args:
            json_path: Path to JSON file
        """
        import json
        with open(json_path, 'r') as f:
            self.layer_map = json.load(f)

    def create_default_mapping(self) -> Dict:
        """
        Tạo default layer mapping cho die-cutting

        Returns:
            Default mapping dictionary
        """
        return {
            'cut': {
                'stroke': 'magenta',
                'stroke_width': 0.1,
                'description': 'Die cut line',
                'color_name': 'CutContour',
                'rgb': [255, 0, 255]
            },
            'score': {
                'stroke': 'cyan',
                'stroke_width': 0.1,
                'description': 'Score/fold line',
                'color_name': 'Score',
                'rgb': [0, 255, 255]
            },
            'kiss_cut': {
                'stroke': 'red',
                'stroke_width': 0.1,
                'description': 'Kiss cut (partial depth)',
                'color_name': 'KissCut',
                'rgb': [255, 0, 0]
            },
            'perf': {
                'stroke': 'blue',
                'stroke_width': 0.1,
                'description': 'Perforation line',
                'color_name': 'Perforation',
                'rgb': [0, 0, 255]
            }
        }
