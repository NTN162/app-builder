@echo off
REM PDF Nesting Runner for Windows
REM Usage: Kéo thả file PDF vào script này

echo ========================================
echo PDF Nesting System - Windows Runner
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate

REM Check if file is provided
if "%~1"=="" (
    echo Error: Vui long keo tha file PDF vao script nay
    echo Hoac chay: run_nesting.bat "path\to\input.pdf"
    pause
    exit /b 1
)

set INPUT_FILE=%~1
set OUTPUT_FILE=%~dpn1_nested.pdf

echo Input: %INPUT_FILE%
echo Output: %OUTPUT_FILE%
echo.

REM Run nesting
python pdf_nesting_pipeline.py "%INPUT_FILE%" "%OUTPUT_FILE%" --sheet-width 1000 --sheet-height 1000 --spacing 5

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo THANH CONG!
    echo Output file: %OUTPUT_FILE%
    echo ========================================
    echo.
    start "" "%OUTPUT_FILE%"
) else (
    echo.
    echo ========================================
    echo LOI! Vui long kiem tra log tren.
    echo ========================================
)

pause
