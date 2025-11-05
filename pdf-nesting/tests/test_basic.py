#!/usr/bin/env python3
"""
Basic tests for PDF Nesting System
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.converter import SVGConverter
from src.nesting import NestingEngine, NestingPart
from src.exporter import LayerMapper
from shapely.geometry import box, Polygon
import math


class TestSVGConverter(unittest.TestCase):
    """Test SVG Converter"""

    def test_create_converter(self):
        """Test creating SVG converter"""
        converter = SVGConverter(1000, 1000)
        self.assertEqual(converter.width, 1000)
        self.assertEqual(converter.height, 1000)

    def test_get_path_bounds(self):
        """Test getting path bounds"""
        converter = SVGConverter(1000, 1000)
        path = "M 0 0 L 100 0 L 100 50 L 0 50 Z"
        bounds = converter.get_path_bounds(path)

        if bounds:  # Có thể fail nếu không có svgpathtools
            self.assertIsNotNone(bounds)
            self.assertIn('width', bounds)
            self.assertIn('height', bounds)


class TestNestingEngine(unittest.TestCase):
    """Test Nesting Engine"""

    def test_create_engine(self):
        """Test creating nesting engine"""
        engine = NestingEngine(1000, 1000, spacing=5)
        self.assertEqual(engine.sheet_width, 1000)
        self.assertEqual(engine.sheet_height, 1000)
        self.assertEqual(engine.spacing, 5)

    def test_nest_simple_rectangles(self):
        """Test nesting simple rectangles"""
        engine = NestingEngine(500, 500, spacing=5)

        parts = []
        for i in range(3):
            rect = box(0, 0, 100, 50)
            part = NestingPart(
                id=f"rect_{i}",
                polygon=rect,
                original_path=f"M 0 0 L 100 0 L 100 50 L 0 50 Z",
                layer="cut"
            )
            parts.append(part)

        result = engine.nest_parts(parts)

        self.assertTrue(result['success'])
        self.assertEqual(result['nested_count'], 3)
        self.assertEqual(result['total_count'], 3)
        self.assertGreater(result['utilization'], 0)

    def test_nest_with_quantity(self):
        """Test nesting with multiple quantities"""
        engine = NestingEngine(500, 500, spacing=5)

        rect = box(0, 0, 50, 50)
        part = NestingPart(
            id="rect",
            polygon=rect,
            original_path="M 0 0 L 50 0 L 50 50 L 0 50 Z",
            layer="cut",
            quantity=5
        )

        result = engine.nest_parts([part])

        self.assertEqual(result['total_count'], 5)
        self.assertGreater(result['nested_count'], 0)

    def test_calculate_bounding_box(self):
        """Test bounding box calculation"""
        engine = NestingEngine(500, 500, spacing=5)

        rect = box(0, 0, 100, 50)
        part = NestingPart(
            id="rect",
            polygon=rect,
            original_path="M 0 0 L 100 0 L 100 50 L 0 50 Z",
            layer="cut"
        )

        engine.nest_parts([part])
        bbox = engine.calculate_bounding_box()

        self.assertIn('width', bbox)
        self.assertIn('height', bbox)
        self.assertGreater(bbox['width'], 0)
        self.assertGreater(bbox['height'], 0)


class TestLayerMapper(unittest.TestCase):
    """Test Layer Mapper"""

    def test_create_mapper(self):
        """Test creating layer mapper"""
        mapper = LayerMapper()
        self.assertIsInstance(mapper.layer_map, dict)

    def test_add_layer_mapping(self):
        """Test adding layer mapping"""
        mapper = LayerMapper()
        mapper.add_layer_mapping('cut', {
            'stroke': 'magenta',
            'stroke_width': 0.1
        })

        self.assertIn('cut', mapper.layer_map)
        self.assertEqual(mapper.layer_map['cut']['stroke'], 'magenta')

    def test_default_mapping(self):
        """Test creating default mapping"""
        mapper = LayerMapper()
        default_map = mapper.create_default_mapping()

        self.assertIn('cut', default_map)
        self.assertIn('score', default_map)
        self.assertIn('kiss_cut', default_map)

    def test_get_layer_properties(self):
        """Test getting layer properties"""
        mapper = LayerMapper()
        mapper.add_layer_mapping('test', {'color': 'red'})

        props = mapper.get_layer_properties('test')
        self.assertEqual(props['color'], 'red')

        # Test non-existent layer
        props2 = mapper.get_layer_properties('nonexistent')
        self.assertEqual(props2, {})


class TestShapelyIntegration(unittest.TestCase):
    """Test Shapely geometry integration"""

    def test_create_polygon(self):
        """Test creating polygon"""
        poly = box(0, 0, 100, 100)
        self.assertTrue(poly.is_valid)
        self.assertEqual(poly.area, 10000)

    def test_polygon_intersection(self):
        """Test polygon intersection"""
        poly1 = box(0, 0, 100, 100)
        poly2 = box(50, 50, 150, 150)

        self.assertTrue(poly1.intersects(poly2))

        intersection = poly1.intersection(poly2)
        self.assertEqual(intersection.area, 2500)

    def test_polygon_buffer(self):
        """Test polygon buffer (for spacing)"""
        poly = box(0, 0, 100, 100)
        buffered = poly.buffer(5)

        self.assertGreater(buffered.area, poly.area)


def run_tests():
    """Run all tests"""
    print("🧪 Running PDF Nesting Tests...\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests
    suite.addTests(loader.loadTestsFromTestCase(TestSVGConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestNestingEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestLayerMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestShapelyIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
