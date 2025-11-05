#!/usr/bin/env python3
"""
PDF Nesting Pipeline
Pipeline hoàn chỉnh: PDF → SVG → Nesting → SVG → PDF/AI

Usage:
    python pdf_nesting_pipeline.py input.pdf output.pdf --sheet-width 1000 --sheet-height 1000
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict
import json

# Import các modules
from src.extractor import PDFShapeExtractor
from src.converter import SVGConverter
from src.nesting import NestingEngine, NestingPart
from src.exporter import PDFExporter, LayerMapper


class PDFNestingPipeline:
    """
    Pipeline hoàn chỉnh cho PDF nesting
    """

    def __init__(self,
                 sheet_width: float = 1000,
                 sheet_height: float = 1000,
                 spacing: float = 5.0,
                 rotation_enabled: bool = True,
                 units: str = 'mm'):
        """
        Initialize pipeline

        Args:
            sheet_width: Chiều rộng sheet đầu ra
            sheet_height: Chiều cao sheet đầu ra
            spacing: Khoảng cách giữa các parts
            rotation_enabled: Cho phép xoay parts
            units: Đơn vị (mm, inch, pt)
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.spacing = spacing
        self.rotation_enabled = rotation_enabled
        self.units = units

        # Components
        self.extractor = None
        self.converter = None
        self.nesting_engine = None
        self.exporter = None
        self.layer_mapper = LayerMapper()

    def run(self,
            input_pdf: str,
            output_path: str,
            output_format: str = 'pdf',
            layer_config: str = None) -> Dict:
        """
        Chạy toàn bộ pipeline

        Args:
            input_pdf: Đường dẫn PDF input
            output_path: Đường dẫn output
            output_format: Format đầu ra ('pdf', 'svg', 'ai')
            layer_config: Path đến file JSON config cho layers

        Returns:
            Dictionary với kết quả
        """
        print(f"🚀 Bắt đầu PDF Nesting Pipeline")
        print(f"📄 Input: {input_pdf}")
        print(f"📦 Output: {output_path} ({output_format})")
        print()

        # Step 1: Extract shapes từ PDF
        print("📍 Step 1: Trích xuất shapes từ PDF...")
        shapes = self._extract_shapes(input_pdf)
        print(f"   ✓ Tìm thấy {len(shapes)} shapes với stroke 'cut'")
        print()

        if not shapes:
            print("❌ Không tìm thấy shapes nào với stroke 'cut'")
            return {'success': False, 'error': 'No cut shapes found'}

        # Step 2: Convert sang SVG và polygons
        print("📍 Step 2: Convert sang SVG format...")
        svg_shapes = self._convert_to_svg(shapes)
        print(f"   ✓ Converted {len(svg_shapes)} shapes sang SVG")
        print()

        # Step 3: Prepare nesting parts
        print("📍 Step 3: Chuẩn bị parts cho nesting...")
        nesting_parts = self._prepare_nesting_parts(svg_shapes)
        print(f"   ✓ Chuẩn bị {len(nesting_parts)} parts")
        print()

        # Step 4: Run nesting algorithm
        print("📍 Step 4: Chạy thuật toán nesting...")
        nesting_result = self._run_nesting(nesting_parts)

        if nesting_result['success']:
            print(f"   ✓ Nest thành công {nesting_result['nested_count']}/{nesting_result['total_count']} parts")
            print(f"   ✓ Utilization: {nesting_result['utilization']:.2f}%")
        else:
            print(f"   ⚠ Nest một phần: {nesting_result['nested_count']}/{nesting_result['total_count']} parts")
            print(f"   ⚠ {len(nesting_result['failed_parts'])} parts không fit")
        print()

        # Step 5: Load layer configuration
        if layer_config:
            print(f"📍 Step 5: Load layer configuration từ {layer_config}...")
            self.layer_mapper.import_layer_mapping(layer_config)
            print("   ✓ Layer mapping loaded")
        else:
            print("📍 Step 5: Sử dụng default layer configuration...")
            self.layer_mapper.layer_map = self.layer_mapper.create_default_mapping()
            print("   ✓ Default mapping created")
        print()

        # Step 6: Export ra format mong muốn
        print(f"📍 Step 6: Export ra {output_format.upper()} format...")
        output_file = self._export_result(
            nesting_result['placed_parts'],
            output_path,
            output_format
        )
        print(f"   ✓ Exported: {output_file}")
        print()

        # Summary
        print("=" * 60)
        print("✅ HOÀN THÀNH!")
        print(f"📊 Thống kê:")
        print(f"   - Input shapes: {len(shapes)}")
        print(f"   - Parts nested: {nesting_result['nested_count']}/{nesting_result['total_count']}")
        print(f"   - Utilization: {nesting_result['utilization']:.2f}%")
        print(f"   - Sheet size: {self.sheet_width} x {self.sheet_height} {self.units}")
        print(f"   - Output: {output_file}")
        print("=" * 60)

        return {
            'success': True,
            'output_file': output_file,
            'stats': {
                'input_shapes': len(shapes),
                'nested_count': nesting_result['nested_count'],
                'total_count': nesting_result['total_count'],
                'utilization': nesting_result['utilization']
            },
            'nesting_result': nesting_result
        }

    def _extract_shapes(self, pdf_path: str) -> List[Dict]:
        """Extract shapes từ PDF"""
        self.extractor = PDFShapeExtractor(pdf_path)
        with self.extractor:
            shapes = self.extractor.extract_all_cut_shapes()
        return shapes

    def _convert_to_svg(self, shapes: List[Dict]) -> List[Dict]:
        """Convert shapes sang SVG"""
        self.converter = SVGConverter(self.sheet_width, self.sheet_height)

        svg_shapes = []
        for shape in shapes:
            svg_shape = {
                'svg_path': shape['svg_path'],
                'layer': shape.get('layer', 'default'),
                'stroke_color': shape.get('stroke_color'),
                'stroke_width': shape.get('stroke_width', 1.0)
            }
            svg_shapes.append(svg_shape)

        return svg_shapes

    def _prepare_nesting_parts(self, svg_shapes: List[Dict]) -> List[NestingPart]:
        """Prepare parts cho nesting"""
        self.nesting_engine = NestingEngine(
            self.sheet_width,
            self.sheet_height,
            self.spacing,
            self.rotation_enabled
        )

        parts = []
        for idx, shape in enumerate(svg_shapes):
            # Convert SVG path sang polygon
            polygon = self.nesting_engine.svg_path_to_polygon(shape['svg_path'])

            if polygon and polygon.is_valid:
                part = NestingPart(
                    id=f"part_{idx}",
                    polygon=polygon,
                    original_path=shape['svg_path'],
                    layer=shape['layer'],
                    rotation_allowed=self.rotation_enabled,
                    metadata={'original_index': idx}
                )
                parts.append(part)
            else:
                print(f"   ⚠ Warning: Shape {idx} không convert được sang polygon")

        return parts

    def _run_nesting(self, parts: List[NestingPart]) -> Dict:
        """Run nesting algorithm"""
        return self.nesting_engine.nest_parts(parts)

    def _export_result(self,
                      placed_parts: List,
                      output_path: str,
                      output_format: str) -> str:
        """Export nested result"""
        self.exporter = PDFExporter(
            self.sheet_width,
            self.sheet_height,
            self.units
        )

        if output_format == 'pdf':
            return self.exporter.export_to_pdf(
                placed_parts,
                output_path,
                self.layer_mapper.layer_map
            )
        elif output_format == 'svg':
            return self.exporter.export_to_svg_with_layers(
                placed_parts,
                output_path,
                self.layer_mapper.layer_map
            )
        elif output_format == 'ai':
            return self.exporter.export_to_illustrator_ai(
                placed_parts,
                output_path,
                self.layer_mapper.layer_map
            )
        else:
            raise ValueError(f"Unsupported output format: {output_format}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='PDF Nesting Pipeline - Tự động sắp xếp khuôn bế từ PDF'
    )

    parser.add_argument('input', help='Input PDF file')
    parser.add_argument('output', help='Output file path')
    parser.add_argument('--sheet-width', type=float, default=1000,
                       help='Chiều rộng sheet (default: 1000)')
    parser.add_argument('--sheet-height', type=float, default=1000,
                       help='Chiều cao sheet (default: 1000)')
    parser.add_argument('--spacing', type=float, default=5.0,
                       help='Khoảng cách giữa parts (default: 5.0)')
    parser.add_argument('--no-rotation', action='store_true',
                       help='Tắt xoay parts')
    parser.add_argument('--units', default='mm', choices=['mm', 'inch', 'pt'],
                       help='Đơn vị (default: mm)')
    parser.add_argument('--format', default='pdf', choices=['pdf', 'svg', 'ai'],
                       help='Output format (default: pdf)')
    parser.add_argument('--layer-config', default=None,
                       help='Path đến file JSON config cho layers')

    args = parser.parse_args()

    # Validate input
    if not Path(args.input).exists():
        print(f"❌ Error: Input file không tồn tại: {args.input}")
        sys.exit(1)

    # Create pipeline
    pipeline = PDFNestingPipeline(
        sheet_width=args.sheet_width,
        sheet_height=args.sheet_height,
        spacing=args.spacing,
        rotation_enabled=not args.no_rotation,
        units=args.units
    )

    # Run pipeline
    try:
        result = pipeline.run(
            args.input,
            args.output,
            args.format,
            args.layer_config
        )

        if result['success']:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
