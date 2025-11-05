#!/usr/bin/env python3
"""
Example Usage - PDF Nesting Pipeline
Ví dụ sử dụng hệ thống nesting
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractor import PDFShapeExtractor
from src.converter import SVGConverter
from src.nesting import NestingEngine, NestingPart
from src.exporter import PDFExporter, LayerMapper


def example_1_basic_usage():
    """
    Ví dụ 1: Sử dụng cơ bản
    Extract shapes từ PDF và export sang SVG
    """
    print("=" * 60)
    print("VÍ DỤ 1: Sử dụng cơ bản - Extract và Export")
    print("=" * 60)

    # Giả sử có file input.pdf
    input_pdf = "input.pdf"

    # Extract shapes
    extractor = PDFShapeExtractor(input_pdf)
    with extractor:
        shapes = extractor.extract_all_cut_shapes()
        print(f"✓ Extracted {len(shapes)} shapes")

        # Get page dimensions
        width, height = extractor.get_page_dimensions()
        print(f"✓ Page size: {width} x {height}")

    # Convert sang SVG
    converter = SVGConverter(width, height)
    svg_file = converter.create_svg_from_shapes(shapes, "output_extracted.svg")
    print(f"✓ Created SVG: {svg_file}")


def example_2_full_nesting():
    """
    Ví dụ 2: Full nesting pipeline
    """
    print("=" * 60)
    print("VÍ DỤ 2: Full Nesting Pipeline")
    print("=" * 60)

    # Configuration
    input_pdf = "input.pdf"
    sheet_width = 1000  # mm
    sheet_height = 1000  # mm
    spacing = 5  # mm

    # Step 1: Extract
    extractor = PDFShapeExtractor(input_pdf)
    with extractor:
        shapes = extractor.extract_all_cut_shapes()

    print(f"✓ Extracted {len(shapes)} shapes")

    # Step 2: Prepare nesting
    nesting_engine = NestingEngine(sheet_width, sheet_height, spacing)

    parts = []
    for idx, shape in enumerate(shapes):
        polygon = nesting_engine.svg_path_to_polygon(shape['svg_path'])
        if polygon:
            part = NestingPart(
                id=f"part_{idx}",
                polygon=polygon,
                original_path=shape['svg_path'],
                layer=shape.get('layer', 'cut')
            )
            parts.append(part)

    print(f"✓ Prepared {len(parts)} parts for nesting")

    # Step 3: Run nesting
    result = nesting_engine.nest_parts(parts)

    print(f"✓ Nested {result['nested_count']}/{result['total_count']} parts")
    print(f"✓ Utilization: {result['utilization']:.2f}%")

    # Step 4: Export
    exporter = PDFExporter(sheet_width, sheet_height, 'mm')

    # Export to PDF
    pdf_output = exporter.export_to_pdf(
        result['placed_parts'],
        "output_nested.pdf"
    )
    print(f"✓ Exported PDF: {pdf_output}")

    # Export to SVG
    svg_output = exporter.export_to_svg_with_layers(
        result['placed_parts'],
        "output_nested.svg"
    )
    print(f"✓ Exported SVG: {svg_output}")


def example_3_layer_mapping():
    """
    Ví dụ 3: Sử dụng layer mapping cho IMP/AE
    """
    print("=" * 60)
    print("VÍ DỤ 3: Layer Mapping cho IMP/AE")
    print("=" * 60)

    # Create layer mapper
    mapper = LayerMapper()

    # Tạo custom layer mapping
    mapper.add_layer_mapping('cut', {
        'stroke': 'magenta',
        'stroke_width': 0.1,
        'color_name': 'CutContour',
        'rgb': [255, 0, 255],
        'description': 'Main die cut line'
    })

    mapper.add_layer_mapping('score', {
        'stroke': 'cyan',
        'stroke_width': 0.1,
        'color_name': 'Score',
        'rgb': [0, 255, 255],
        'description': 'Score/fold line'
    })

    mapper.add_layer_mapping('perforation', {
        'stroke': 'blue',
        'stroke_width': 0.1,
        'color_name': 'Perf',
        'rgb': [0, 0, 255],
        'description': 'Perforation line'
    })

    # Export mapping
    mapper.export_layer_mapping('layer_config.json')
    print("✓ Exported layer mapping to layer_config.json")

    # Load lại
    mapper2 = LayerMapper()
    mapper2.import_layer_mapping('layer_config.json')
    print("✓ Imported layer mapping")

    # Show layers
    for layer_name, props in mapper2.layer_map.items():
        print(f"  - {layer_name}: {props['description']}")


def example_4_custom_shapes():
    """
    Ví dụ 4: Tạo shapes custom và nest
    """
    print("=" * 60)
    print("VÍ DỤ 4: Custom Shapes")
    print("=" * 60)

    from shapely.geometry import box, Polygon
    import math

    # Tạo các shapes đơn giản
    nesting_engine = NestingEngine(500, 500, spacing=5)

    parts = []

    # Rectangle 1
    rect1 = box(0, 0, 100, 50)
    parts.append(NestingPart(
        id="rect1",
        polygon=rect1,
        original_path="M 0 0 L 100 0 L 100 50 L 0 50 Z",
        layer="cut",
        quantity=5  # 5 copies
    ))

    # Circle (approximated as polygon)
    circle_points = []
    for i in range(32):
        angle = 2 * math.pi * i / 32
        x = 30 * math.cos(angle) + 30
        y = 30 * math.sin(angle) + 30
        circle_points.append((x, y))

    circle = Polygon(circle_points)
    parts.append(NestingPart(
        id="circle1",
        polygon=circle,
        original_path="M 60 30 A 30 30 0 1 1 59.999 30",
        layer="cut",
        quantity=10  # 10 copies
    ))

    # Nest
    result = nesting_engine.nest_parts(parts)

    print(f"✓ Created {len(parts)} part types")
    print(f"✓ Total parts to nest: {result['total_count']}")
    print(f"✓ Successfully nested: {result['nested_count']}")
    print(f"✓ Utilization: {result['utilization']:.2f}%")

    # Export
    exporter = PDFExporter(500, 500, 'mm')
    output = exporter.export_to_pdf(result['placed_parts'], "custom_shapes.pdf")
    print(f"✓ Exported: {output}")


if __name__ == '__main__':
    print("\n🎯 PDF NESTING - VÍ DỤ SỬ DỤNG\n")

    # Chạy ví dụ 3 (layer mapping) vì không cần file input
    example_3_layer_mapping()

    # Chạy ví dụ 4 (custom shapes)
    print("\n")
    example_4_custom_shapes()

    print("\n" + "=" * 60)
    print("✅ Hoàn thành! Xem các file output đã tạo.")
    print("=" * 60)
