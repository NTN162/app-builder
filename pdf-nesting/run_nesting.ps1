# PDF Nesting PowerShell Script
# Usage: .\run_nesting.ps1 -InputFile "input.pdf" -SheetWidth 1000 -SheetHeight 1000

param(
    [Parameter(Mandatory=$true)]
    [string]$InputFile,

    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "",

    [Parameter(Mandatory=$false)]
    [int]$SheetWidth = 1000,

    [Parameter(Mandatory=$false)]
    [int]$SheetHeight = 1000,

    [Parameter(Mandatory=$false)]
    [int]$Spacing = 5,

    [Parameter(Mandatory=$false)]
    [string]$Format = "pdf",

    [Parameter(Mandatory=$false)]
    [switch]$NoRotation
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PDF Nesting System - PowerShell Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if input file exists
if (-not (Test-Path $InputFile)) {
    Write-Host "Error: Input file not found: $InputFile" -ForegroundColor Red
    exit 1
}

# Generate output filename if not provided
if ($OutputFile -eq "") {
    $dir = [System.IO.Path]::GetDirectoryName($InputFile)
    $name = [System.IO.Path]::GetFileNameWithoutExtension($InputFile)
    $OutputFile = Join-Path $dir "${name}_nested.$Format"
}

Write-Host "Input:  $InputFile" -ForegroundColor Green
Write-Host "Output: $OutputFile" -ForegroundColor Green
Write-Host "Sheet:  ${SheetWidth}x${SheetHeight} mm" -ForegroundColor Yellow
Write-Host "Spacing: $Spacing mm" -ForegroundColor Yellow
Write-Host ""

# Activate virtual environment
$venvActivate = "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & $venvActivate
}

# Build command
$args = @(
    "pdf_nesting_pipeline.py",
    $InputFile,
    $OutputFile,
    "--sheet-width", $SheetWidth,
    "--sheet-height", $SheetHeight,
    "--spacing", $Spacing,
    "--format", $Format
)

if ($NoRotation) {
    $args += "--no-rotation"
}

# Run nesting
Write-Host "Running nesting algorithm..." -ForegroundColor Cyan
Write-Host ""

& python $args

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "SUCCESS!" -ForegroundColor Green
    Write-Host "Output file: $OutputFile" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""

    # Open output file
    $response = Read-Host "Open output file? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Start-Process $OutputFile
    }
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "ERROR! Check log above." -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
