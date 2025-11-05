# Hướng dẫn Cài đặt
# PDF Nesting System Installation Guide

## Yêu cầu hệ thống

- **Python**: 3.8 hoặc cao hơn
- **OS**: Linux, macOS, hoặc Windows
- **RAM**: Tối thiểu 2GB (khuyến nghị 4GB+ cho file PDF lớn)
- **Disk**: 500MB cho dependencies

## Cài đặt

### Bước 1: Clone hoặc Download Project

```bash
cd /path/to/your/projects
# Nếu từ git
git clone <repository-url> pdf-nesting
cd pdf-nesting

# Hoặc giải nén file zip đã download
unzip pdf-nesting.zip
cd pdf-nesting
```

### Bước 2: Tạo Virtual Environment (Khuyến nghị)

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt (Linux/macOS)
source venv/bin/activate

# Kích hoạt (Windows)
venv\Scripts\activate
```

### Bước 3: Cài đặt Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Cài đặt requirements
pip install -r requirements.txt
```

### Bước 4: (Optional) Cài đặt Package

```bash
# Development installation
pip install -e .

# Sau đó có thể dùng command:
pdf-nesting input.pdf output.pdf --sheet-width 1000 --sheet-height 1000
```

## Kiểm tra Cài đặt

### Chạy Tests

```bash
python tests/test_basic.py
```

Nếu thấy:
```
✅ All tests passed!
```

Thì cài đặt thành công!

### Chạy Example

```bash
python examples/example_usage.py
```

Nếu chạy không lỗi và tạo được file `custom_shapes.pdf`, cài đặt đã hoàn tất.

## Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'fitz'"

PyMuPDF cần được cài đặt:

```bash
pip install PyMuPDF
```

### Lỗi: "ImportError: cannot import name 'parse_path'"

svgpathtools cần được cài:

```bash
pip install svgpathtools
```

### Lỗi: "shapely.errors.TopologicalError"

Shapely có issue, thử upgrade:

```bash
pip install --upgrade shapely
```

### Lỗi khi cài reportlab trên Windows

Cần Visual C++ Build Tools. Download từ:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

Hoặc dùng wheel prebuilt:

```bash
pip install --only-binary :all: reportlab
```

### Lỗi Memory khi xử lý PDF lớn

Giảm số shapes hoặc tăng RAM. Có thể process từng page:

```python
# Trong code
extractor.extract_paths_from_page(page_num=0)  # Chỉ page đầu tiên
```

## Cài đặt Optional Dependencies

### Để xuất DXF (AutoCAD):

```bash
pip install ezdxf
```

### Để xử lý PDF phức tạp hơn:

```bash
pip install pikepdf
```

### Development tools:

```bash
pip install pytest black flake8 mypy
```

## Cài đặt trên các HĐH khác nhau

### Ubuntu/Debian Linux

```bash
# System dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Install project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### macOS

```bash
# Cài Homebrew nếu chưa có
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Cài Python
brew install python@3.11

# Install project
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

1. Download Python từ https://www.python.org/downloads/
2. Chạy installer, check "Add Python to PATH"
3. Mở Command Prompt hoặc PowerShell:

```cmd
cd pdf-nesting
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Cập nhật

Để cập nhật dependencies:

```bash
pip install --upgrade -r requirements.txt
```

## Gỡ cài đặt

```bash
# Deactivate virtual environment
deactivate

# Xóa thư mục
cd ..
rm -rf pdf-nesting  # Linux/macOS
# hoặc
rmdir /s pdf-nesting  # Windows
```

## Docker (Alternative)

Nếu muốn dùng Docker:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "pdf_nesting_pipeline.py"]
```

Build và run:

```bash
docker build -t pdf-nesting .
docker run -v $(pwd):/data pdf-nesting /data/input.pdf /data/output.pdf
```

## Hỗ trợ

Nếu gặp vấn đề, tạo issue trên GitHub với thông tin:

- OS và version
- Python version (`python --version`)
- Full error message
- Output của `pip list`

---

Happy nesting! 🎯
