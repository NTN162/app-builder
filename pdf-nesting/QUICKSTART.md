# Quick Start Guide
# Hướng dẫn Nhanh

Bắt đầu với PDF Nesting System trong 5 phút!

## 🚀 Cài đặt Nhanh

```bash
cd pdf-nesting
pip install -r requirements.txt
```

## 💡 Sử dụng Cơ bản

### Cách 1: Command Line (Đơn giản nhất)

```bash
python pdf_nesting_pipeline.py input.pdf output.pdf \
    --sheet-width 1000 \
    --sheet-height 1000
```

### Cách 2: Python Script

Tạo file `my_nesting.py`:

```python
from pdf_nesting_pipeline import PDFNestingPipeline

pipeline = PDFNestingPipeline(
    sheet_width=1000,  # mm
    sheet_height=1000, # mm
    spacing=5          # khoảng cách giữa parts
)

result = pipeline.run(
    input_pdf='input.pdf',
    output_path='output.pdf',
    output_format='pdf'
)

print(f"✅ Done! Utilization: {result['stats']['utilization']:.1f}%")
```

Chạy:

```bash
python my_nesting.py
```

## 📝 Các Ví dụ Thực tế

### Ví dụ 1: Nest và xuất PDF

```bash
python pdf_nesting_pipeline.py \
    die_cut_shapes.pdf \
    nested_output.pdf \
    --sheet-width 1200 \
    --sheet-height 800 \
    --spacing 10
```

### Ví dụ 2: Xuất sang SVG (để edit trong Illustrator)

```bash
python pdf_nesting_pipeline.py \
    input.pdf \
    output.svg \
    --format svg \
    --sheet-width 1000 \
    --sheet-height 1000
```

### Ví dụ 3: Không cho xoay parts

```bash
python pdf_nesting_pipeline.py \
    input.pdf \
    output.pdf \
    --no-rotation
```

### Ví dụ 4: Sử dụng custom layer config

```bash
# Tạo layer config trước
python -c "
from src.exporter import LayerMapper
m = LayerMapper()
m.layer_map = m.create_default_mapping()
m.export_layer_mapping('my_layers.json')
print('✓ Created my_layers.json')
"

# Sau đó dùng config này
python pdf_nesting_pipeline.py \
    input.pdf \
    output.pdf \
    --layer-config my_layers.json
```

## 🎯 Workflow Thực tế

### Workflow 1: Từ Illustrator → Nesting → Quay lại Illustrator

```bash
# 1. Export từ Illustrator sang PDF
# (File → Save As → PDF, đảm bảo stroke có tên 'cut')

# 2. Chạy nesting
python pdf_nesting_pipeline.py \
    illustrator_export.pdf \
    nested.svg \
    --format svg \
    --sheet-width 1000 \
    --sheet-height 1500

# 3. Mở nested.svg trong Illustrator
# (File → Open → nested.svg)

# 4. Gửi máy cắt CNC/Laser
```

### Workflow 2: Batch Processing nhiều files

Tạo script `batch_nest.py`:

```python
from pdf_nesting_pipeline import PDFNestingPipeline
from pathlib import Path

# Tìm tất cả PDF files
input_dir = Path('input_pdfs')
output_dir = Path('output_nested')
output_dir.mkdir(exist_ok=True)

pipeline = PDFNestingPipeline(
    sheet_width=1000,
    sheet_height=1000,
    spacing=5
)

for pdf_file in input_dir.glob('*.pdf'):
    output_file = output_dir / f'nested_{pdf_file.name}'

    print(f'Processing {pdf_file.name}...')

    result = pipeline.run(
        str(pdf_file),
        str(output_file),
        output_format='pdf'
    )

    print(f'  ✓ Utilization: {result["stats"]["utilization"]:.1f}%\n')

print('✅ All files processed!')
```

Chạy:

```bash
python batch_nest.py
```

## 🔧 Tùy chỉnh Nhanh

### Thay đổi màu cut stroke

Edit file `src/extractor/pdf_extractor.py`, method `_is_cut_stroke()`:

```python
def _is_cut_stroke(self, color, name):
    # Thêm màu của bạn
    if name and 'mycut' in name.lower():
        return True

    # Thêm RGB color
    if color and self._is_my_color(color):
        return True

    return False

def _is_my_color(self, color):
    # Check for your specific RGB
    # Ví dụ: green (0, 1, 0)
    return (len(color) >= 3 and
            color[0] < 0.1 and
            color[1] > 0.9 and
            color[2] < 0.1)
```

### Thêm layer mới

```python
from src.exporter import LayerMapper

mapper = LayerMapper()
mapper.add_layer_mapping('die_cut', {
    'stroke': 'magenta',
    'stroke_width': 0.1,
    'description': 'Die cut line'
})

mapper.add_layer_mapping('crease', {
    'stroke': 'blue',
    'stroke_width': 0.05,
    'description': 'Crease line'
})

mapper.export_layer_mapping('custom_layers.json')
```

## 📊 Hiểu Output

Khi chạy pipeline, bạn sẽ thấy:

```
🚀 Bắt đầu PDF Nesting Pipeline
📄 Input: input.pdf
📦 Output: output.pdf (pdf)

📍 Step 1: Trích xuất shapes từ PDF...
   ✓ Tìm thấy 24 shapes với stroke 'cut'

📍 Step 2: Convert sang SVG format...
   ✓ Converted 24 shapes sang SVG

📍 Step 3: Chuẩn bị parts cho nesting...
   ✓ Chuẩn bị 24 parts

📍 Step 4: Chạy thuật toán nesting...
   ✓ Nest thành công 24/24 parts
   ✓ Utilization: 67.23%

📍 Step 5: Sử dụng default layer configuration...
   ✓ Default mapping created

📍 Step 6: Export ra PDF format...
   ✓ Exported: output.pdf

============================================================
✅ HOÀN THÀNH!
📊 Thống kê:
   - Input shapes: 24
   - Parts nested: 24/24
   - Utilization: 67.23%
   - Sheet size: 1000 x 1000 mm
   - Output: output.pdf
============================================================
```

**Utilization**: % diện tích sheet được sử dụng. Càng cao càng tốt!

- **< 50%**: Kém, sheet quá lớn hoặc parts quá lớn/ít
- **50-70%**: OK, chấp nhận được
- **70-85%**: Tốt, tối ưu tốt
- **> 85%**: Rất tốt, gần như optimal

## 🐛 Xử lý Lỗi Thường gặp

### Lỗi: "No cut shapes found"

**Nguyên nhân**: PDF không có shapes với stroke 'cut'

**Giải pháp**:
1. Kiểm tra PDF có vector paths không (không phải raster image)
2. Kiểm tra stroke color phải là magenta hoặc cyan
3. Thử mở PDF trong Illustrator, đảm bảo có paths không bị rasterized

### Lỗi: "Parts không fit vào sheet"

**Nguyên nhân**: Sheet quá nhỏ cho các parts

**Giải pháp**:
```bash
# Tăng kích thước sheet
python pdf_nesting_pipeline.py input.pdf output.pdf \
    --sheet-width 2000 \
    --sheet-height 2000
```

### Warning: "Shape X không convert được sang polygon"

**Nguyên nhân**: Path quá phức tạp hoặc invalid

**Giải pháp**: Trong Illustrator, simplify path trước khi export:
- Object → Path → Simplify
- Giảm số anchor points

## 💪 Best Practices

1. **Chuẩn bị PDF tốt**:
   - Sử dụng vector paths, không rasterize
   - Stroke width thin (0.1pt - 0.5pt)
   - Màu rõ ràng (magenta cho cut)

2. **Chọn sheet size hợp lý**:
   - Dựa trên kích thước vật liệu thật
   - Leave margin 10-20mm

3. **Test trước**:
   - Test với 1-2 shapes trước
   - Kiểm tra output trong Illustrator
   - Verify spacing đủ lớn

4. **Optimize utilization**:
   - Cho phép rotation (`--no-rotation` OFF)
   - Giảm spacing nếu máy cắt chính xác
   - Group các parts cùng size

## 🎓 Học Thêm

- Đọc [README.md](README.md) để hiểu chi tiết
- Đọc [INSTALL.md](INSTALL.md) nếu gặp vấn đề cài đặt
- Xem [examples/example_usage.py](examples/example_usage.py) cho ví dụ nâng cao
- Đọc code trong `src/` để customize

## 🆘 Cần Giúp?

1. Chạy tests: `python tests/test_basic.py`
2. Chạy examples: `python examples/example_usage.py`
3. Check issues trên GitHub
4. Đọc docstrings trong code

---

**Chúc bạn nesting hiệu quả! 🎯**
