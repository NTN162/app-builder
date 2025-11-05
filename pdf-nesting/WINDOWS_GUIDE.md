# 🪟 Hướng dẫn Hoàn chỉnh cho Windows
# PDF Nesting System - Windows Guide

## 📋 Mục lục

1. [Cài đặt Python](#1-cài-đặt-python)
2. [Cài đặt Project](#2-cài-đặt-project)
3. [Cách Chạy](#3-cách-chạy)
4. [Troubleshooting](#4-troubleshooting)
5. [Tips & Tricks](#5-tips--tricks)

---

## 1. Cài đặt Python

### Bước 1.1: Download Python

1. Vào https://www.python.org/downloads/
2. Download phiên bản **Python 3.11.x** (hoặc 3.10.x, 3.9.x, 3.8.x)
3. Chọn "Windows installer (64-bit)"

### Bước 1.2: Cài đặt

1. Chạy file installer đã download
2. **✅ QUAN TRỌNG**: TICK vào ô **"Add Python to PATH"**
3. Click "Install Now"
4. Đợi cài đặt hoàn tất
5. Click "Close"

### Bước 1.3: Verify

Mở **Command Prompt**:
- Nhấn `Win + R`
- Gõ `cmd`
- Enter

Trong Command Prompt, gõ:
```cmd
python --version
```

Phải thấy: `Python 3.x.x`

Nếu không thấy, reboot máy và thử lại.

---

## 2. Cài đặt Project

### Bước 2.1: Download Project

**Option A: Có Git**
```cmd
cd C:\Users\YourName\Documents
git clone https://github.com/NTN162/app-builder.git
cd app-builder\pdf-nesting
```

**Option B: Không có Git**
1. Download ZIP từ GitHub
2. Giải nén vào `C:\Users\YourName\Documents\`
3. Vào folder `app-builder\pdf-nesting`

### Bước 2.2: Tạo Virtual Environment

Mở Command Prompt tại folder `pdf-nesting`:

```cmd
:: Tạo virtual environment
python -m venv venv

:: Kích hoạt
venv\Scripts\activate
```

Bạn sẽ thấy `(venv)` xuất hiện trước dòng lệnh.

**Nếu gặp lỗi "cannot be loaded because running scripts is disabled":**

Mở **PowerShell as Administrator**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Sau đó đóng PowerShell, quay lại Command Prompt và thử lại.

### Bước 2.3: Cài đặt Dependencies

```cmd
:: Upgrade pip
python -m pip install --upgrade pip

:: Cài đặt packages
pip install -r requirements.txt
```

**Quá trình này mất 3-5 phút**. Chờ đến khi hoàn tất.

### Bước 2.4: Test Cài đặt

```cmd
python tests\test_basic.py
```

Nếu thấy `✅ All tests passed!` → Thành công!

---

## 3. Cách Chạy

### 🎯 Cách 1: Command Line (Cơ bản)

```cmd
python pdf_nesting_pipeline.py input.pdf output.pdf --sheet-width 1000 --sheet-height 1000
```

**Ví dụ với đường dẫn đầy đủ:**
```cmd
python pdf_nesting_pipeline.py ^
    "C:\Users\John\Desktop\my_shapes.pdf" ^
    "C:\Users\John\Desktop\nested_output.pdf" ^
    --sheet-width 1200 ^
    --sheet-height 800 ^
    --spacing 10
```

**Lưu ý:**
- Dùng `^` để xuống dòng (không phải `\`)
- Dùng `"` nếu path có khoảng trắng
- Đường dẫn Windows dùng `\` (không phải `/`)

### 🖱️ Cách 2: Batch File (Kéo thả)

1. Click đúp vào file `run_nesting.bat`
2. Kéo thả file PDF vào cửa sổ
3. Đợi xử lý xong
4. File output tự động mở

**Hoặc:**
```cmd
run_nesting.bat "C:\path\to\input.pdf"
```

### 💻 Cách 3: PowerShell Script

```powershell
.\run_nesting.ps1 -InputFile "input.pdf" -SheetWidth 1200 -SheetHeight 800
```

**Các tham số:**
```powershell
.\run_nesting.ps1 `
    -InputFile "C:\path\to\input.pdf" `
    -OutputFile "C:\path\to\output.pdf" `
    -SheetWidth 1000 `
    -SheetHeight 1000 `
    -Spacing 5 `
    -Format "pdf" `
    -NoRotation
```

### 🎨 Cách 4: GUI Interface (Dễ nhất!)

```cmd
python gui_launcher.py
```

Giao diện GUI sẽ mở:
1. Click "Browse..." để chọn file PDF input
2. Chọn output location
3. Điều chỉnh sheet size, spacing
4. Click "▶ Run Nesting"
5. Đợi xong, file tự động mở!

---

## 4. Troubleshooting

### ❌ Lỗi: "python is not recognized"

**Nguyên nhân:** Python chưa được add vào PATH

**Giải pháp:**
1. Cài lại Python, nhớ tick "Add Python to PATH"
2. Hoặc add manually:
   - `Win + R` → `sysdm.cpl` → Enter
   - Tab "Advanced" → "Environment Variables"
   - Trong "System variables", chọn "Path" → Edit
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts`
   - Click OK, restart Command Prompt

### ❌ Lỗi: "pip install" fails

**Nguyên nhân:** Network issues hoặc thiếu compiler

**Giải pháp:**

**Option 1: Sử dụng prebuilt wheels**
```cmd
pip install --only-binary :all: reportlab Pillow shapely
```

**Option 2: Install Visual C++ Build Tools**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Chạy installer
3. Chọn "Desktop development with C++"
4. Install (mất 15-30 phút)
5. Restart Command Prompt
6. Chạy lại `pip install -r requirements.txt`

### ❌ Lỗi: "No module named 'fitz'"

**Nguyên nhân:** PyMuPDF chưa được cài

**Giải pháp:**
```cmd
pip install PyMuPDF
```

### ❌ Lỗi: "cannot be loaded because running scripts is disabled"

**Nguyên nhân:** PowerShell execution policy

**Giải pháp:**

Mở PowerShell **as Administrator**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Gõ `Y` để confirm.

### ❌ Lỗi: "No cut shapes found"

**Nguyên nhân:** PDF không có shapes với stroke "cut"

**Giải pháp:**
1. Mở PDF trong Adobe Illustrator
2. Đảm bảo shapes là **vector paths** (không phải images)
3. Set stroke color = **magenta** (255, 0, 255) hoặc **cyan** (0, 255, 255)
4. Hoặc đặt tên layer chứa "cut"
5. Save lại PDF

### ❌ Lỗi: "Parts không fit vào sheet"

**Nguyên nhân:** Sheet size quá nhỏ

**Giải pháp:**
```cmd
:: Tăng sheet size
python pdf_nesting_pipeline.py input.pdf output.pdf --sheet-width 2000 --sheet-height 2000
```

### ❌ Lỗi: Memory error

**Nguyên nhân:** PDF quá lớn

**Giải pháp:**
1. Giảm resolution của PDF
2. Simplify paths trong Illustrator
3. Process từng page riêng

---

## 5. Tips & Tricks

### 💡 Tip 1: Tạo Desktop Shortcut

1. Right-click `gui_launcher.py` → Send to → Desktop (create shortcut)
2. Right-click shortcut → Properties
3. Target: `C:\...\venv\Scripts\python.exe C:\...\gui_launcher.py`
4. Start in: `C:\...\pdf-nesting`
5. Change icon nếu muốn
6. Click OK

Giờ chỉ cần double-click shortcut là chạy!

### 💡 Tip 2: Batch Processing nhiều files

Tạo file `batch_process.bat`:

```batch
@echo off
for %%f in (*.pdf) do (
    echo Processing %%f...
    python pdf_nesting_pipeline.py "%%f" "%%~nf_nested.pdf" --sheet-width 1000 --sheet-height 1000
)
echo Done!
pause
```

Đặt file này trong folder chứa PDF files, double-click để chạy.

### 💡 Tip 3: Tích hợp với File Explorer

Tạo Context Menu để right-click PDF → "Nest PDF":

1. Tạo file `nest_pdf.reg`:

```reg
Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\NestPDF]
@="Nest PDF"

[HKEY_CLASSES_ROOT\SystemFileAssociations\.pdf\shell\NestPDF\command]
@="\"C:\\Users\\YourName\\Documents\\app-builder\\pdf-nesting\\run_nesting.bat\" \"%1\""
```

2. Sửa đường dẫn cho đúng
3. Double-click file .reg để import
4. Giờ right-click PDF → thấy "Nest PDF"!

### 💡 Tip 4: Watch Folder (Auto-process)

Tạo file `watch_folder.py`:

```python
import time
from pathlib import Path
from pdf_nesting_pipeline import PDFNestingPipeline

watch_dir = Path(r"C:\Users\YourName\Desktop\watch")
output_dir = Path(r"C:\Users\YourName\Desktop\output")

pipeline = PDFNestingPipeline(1000, 1000, 5)

print(f"Watching {watch_dir}...")

processed = set()

while True:
    for pdf in watch_dir.glob("*.pdf"):
        if pdf not in processed:
            print(f"Processing {pdf.name}...")
            output = output_dir / f"nested_{pdf.name}"
            try:
                pipeline.run(str(pdf), str(output), 'pdf')
                processed.add(pdf)
                print(f"✓ Done: {output}")
            except Exception as e:
                print(f"✗ Error: {e}")

    time.sleep(5)  # Check every 5 seconds
```

Chạy: `python watch_folder.py`

### 💡 Tip 5: Export cài đặt

Tạo file `config.json` với settings thường dùng:

```json
{
  "sheet_width": 1200,
  "sheet_height": 800,
  "spacing": 10,
  "rotation_enabled": true,
  "output_format": "pdf",
  "units": "mm"
}
```

Load trong script:
```python
import json
with open('config.json') as f:
    config = json.load(f)

pipeline = PDFNestingPipeline(**config)
```

---

## 📞 Cần Thêm Hỗ trợ?

### Checklist trước khi hỏi:

- [ ] Đã chạy `python tests\test_basic.py` chưa?
- [ ] Đã thử `python examples\example_usage.py` chưa?
- [ ] Có error message gì? (copy full text)
- [ ] Python version? (`python --version`)
- [ ] Output của `pip list` là gì?

### Resources:

- README.md - Documentation chính
- QUICKSTART.md - Quick start
- INSTALL.md - Cài đặt chi tiết
- PROJECT_SUMMARY.md - Technical details

### Common Commands:

```cmd
:: Activate environment
venv\Scripts\activate

:: Deactivate environment
deactivate

:: Update packages
pip install --upgrade -r requirements.txt

:: Clear cache
pip cache purge

:: List installed packages
pip list

:: Uninstall everything
pip freeze > installed.txt
pip uninstall -r installed.txt -y
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Chạy GUI | `python gui_launcher.py` |
| Chạy CLI | `python pdf_nesting_pipeline.py input.pdf output.pdf` |
| Batch file | `run_nesting.bat "input.pdf"` |
| PowerShell | `.\run_nesting.ps1 -InputFile "input.pdf"` |
| Run tests | `python tests\test_basic.py` |
| Run examples | `python examples\example_usage.py` |
| Activate venv | `venv\Scripts\activate` |
| Deactivate | `deactivate` |

---

**Happy nesting on Windows! 🪟🎯**
