# PDF Nesting System
# Hệ thống Nesting File PDF theo Hình Dạng Khuôn Bế

Hệ thống tự động trích xuất và sắp xếp các hình dạng khuôn bế từ file PDF, tối ưu hóa việc sử dụng vật liệu.

## 🎯 Tính năng

- ✅ **Trích xuất tự động** hình dạng có stroke màu "cut" từ PDF
- ✅ **Nesting thông minh** sử dụng thuật toán Bottom-Left với rotation
- ✅ **Hỗ trợ layers** để phân loại các loại cắt (cut, score, perforation, etc.)
- ✅ **Export đa định dạng**: PDF, SVG, AI (Adobe Illustrator)
- ✅ **Layer mapping** tương thích với IMP/AE (Illustrator/After Effects)
- ✅ **Tối ưu hóa vật liệu** với tính toán utilization

## 🏗️ Kiến trúc

Flow xử lý:

```
PDF Input → Extract Shapes → Convert to SVG → Nesting Algorithm → Export → PDF/SVG/AI Output
```

### Các Module

1. **PDF Extractor** (`src/extractor/`): Trích xuất shapes từ PDF
2. **SVG Converter** (`src/converter/`): Chuyển đổi giữa PDF paths và SVG
3. **Nesting Engine** (`src/nesting/`): Thuật toán sắp xếp tối ưu
4. **PDF/AI Exporter** (`src/exporter/`): Export ra các format

## 📦 Cài đặt

### Yêu cầu

- Python 3.8+
- pip hoặc conda

### Cài đặt dependencies

```bash
cd pdf-nesting
pip install -r requirements.txt
```

## 🚀 Sử dụng

### Cách 1: Sử dụng Pipeline Script

```bash
python pdf_nesting_pipeline.py input.pdf output.pdf \
    --sheet-width 1000 \
    --sheet-height 1000 \
    --spacing 5 \
    --format pdf
```

#### Tham số:

- `input`: File PDF input
- `output`: File output (PDF/SVG/AI)
- `--sheet-width`: Chiều rộng sheet (default: 1000)
- `--sheet-height`: Chiều cao sheet (default: 1000)
- `--spacing`: Khoảng cách giữa parts (default: 5.0)
- `--no-rotation`: Tắt xoay parts
- `--units`: Đơn vị (mm/inch/pt, default: mm)
- `--format`: Format output (pdf/svg/ai, default: pdf)
- `--layer-config`: File JSON config cho layers

### Cách 2: Sử dụng trong Python

```python
from pdf_nesting_pipeline import PDFNestingPipeline

# Tạo pipeline
pipeline = PDFNestingPipeline(
    sheet_width=1000,
    sheet_height=1000,
    spacing=5.0,
    rotation_enabled=True,
    units='mm'
)

# Chạy pipeline
result = pipeline.run(
    input_pdf='input.pdf',
    output_path='output.pdf',
    output_format='pdf'
)

print(f"Utilization: {result['stats']['utilization']:.2f}%")
```

### Cách 3: Sử dụng Module riêng lẻ

```python
from src.extractor import PDFShapeExtractor
from src.nesting import NestingEngine, NestingPart
from src.exporter import PDFExporter

# Extract shapes
extractor = PDFShapeExtractor('input.pdf')
with extractor:
    shapes = extractor.extract_all_cut_shapes()

# Prepare nesting
engine = NestingEngine(1000, 1000, spacing=5)
parts = []
for idx, shape in enumerate(shapes):
    polygon = engine.svg_path_to_polygon(shape['svg_path'])
    if polygon:
        part = NestingPart(
            id=f"part_{idx}",
            polygon=polygon,
            original_path=shape['svg_path'],
            layer=shape.get('layer', 'cut')
        )
        parts.append(part)

# Run nesting
result = engine.nest_parts(parts)

# Export
exporter = PDFExporter(1000, 1000, 'mm')
exporter.export_to_pdf(result['placed_parts'], 'output.pdf')
```

## 🎨 Layer Configuration

### Tạo Layer Config

```python
from src.exporter import LayerMapper

mapper = LayerMapper()

# Thêm layer
mapper.add_layer_mapping('cut', {
    'stroke': 'magenta',
    'stroke_width': 0.1,
    'color_name': 'CutContour',
    'rgb': [255, 0, 255],
    'description': 'Die cut line'
})

# Export ra JSON
mapper.export_layer_mapping('layers.json')
```

### Sử dụng Layer Config

```bash
python pdf_nesting_pipeline.py input.pdf output.pdf --layer-config layers.json
```

### Default Layers

Hệ thống có sẵn các layer mặc định:

- **cut**: Đường cắt chính (magenta)
- **score**: Đường nếp gấp (cyan)
- **kiss_cut**: Cắt một phần độ sâu (red)
- **perf**: Đường đục lỗ (blue)

## 📊 Output

Pipeline sẽ tạo ra:

1. **Nested PDF/SVG/AI**: File chứa các shapes đã được sắp xếp
2. **Statistics**: Thống kê về số parts, utilization, etc.
3. **Layer information**: Metadata về layers

Example output:

```
✅ HOÀN THÀNH!
📊 Thống kê:
   - Input shapes: 24
   - Parts nested: 24/24
   - Utilization: 67.23%
   - Sheet size: 1000 x 1000 mm
   - Output: output_nested.pdf
```

## 🔧 Tùy chỉnh

### Điều chỉnh Nesting Algorithm

File: `src/nesting/nesting_engine.py`

- Thay đổi `rotation_step`: Số độ mỗi bước xoay
- Thay đổi sorting: Sắp xếp parts theo chiều cao, diện tích, etc.
- Implement các heuristic khác: Best-Fit, First-Fit, etc.

### Thêm Output Format

File: `src/exporter/pdf_exporter.py`

Thêm method mới:

```python
def export_to_dxf(self, placed_parts, output_path):
    # Implementation cho DXF format
    pass
```

## 📁 Cấu trúc Project

```
pdf-nesting/
├── src/
│   ├── extractor/
│   │   ├── __init__.py
│   │   └── pdf_extractor.py      # Extract shapes từ PDF
│   ├── converter/
│   │   ├── __init__.py
│   │   └── svg_converter.py      # Convert PDF ↔ SVG
│   ├── nesting/
│   │   ├── __init__.py
│   │   └── nesting_engine.py     # Thuật toán nesting
│   └── exporter/
│       ├── __init__.py
│       └── pdf_exporter.py       # Export PDF/SVG/AI
├── examples/
│   └── example_usage.py          # Ví dụ sử dụng
├── tests/
│   └── (test files)
├── pdf_nesting_pipeline.py       # Main pipeline script
├── requirements.txt              # Dependencies
└── README.md                     # Tài liệu này
```

## 🧪 Testing

Chạy examples:

```bash
cd pdf-nesting
python examples/example_usage.py
```

## 🤝 Đóng góp

Dựa trên ý tưởng từ [Packaide](https://github.com/DanielLiamAnderson/Packaide)

## 📄 License

Apache 2.0

## 🐛 Known Issues

1. **Curve approximation**: Các đường cong phức tạp có thể được approximated
2. **Memory usage**: File PDF lớn có thể cần nhiều RAM
3. **Nesting optimality**: Thuật toán sử dụng heuristic, không đảm bảo optimal

## 🔮 Roadmap

- [ ] Hỗ trợ multi-sheet nesting
- [ ] Genetic algorithm cho nesting tốt hơn
- [ ] GPU acceleration
- [ ] Web interface
- [ ] Batch processing
- [ ] Cloud integration

## 📞 Support

Để báo lỗi hoặc đề xuất tính năng, tạo issue trên GitHub.

---

**Made with ❤️ for die-cutting optimization**
