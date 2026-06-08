# YouTube Video Downloader - Build Script (PowerShell)
# Usage: .\build.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "YouTube Video Downloader - Build Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "1. Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Please install Python from https://www.python.org" -ForegroundColor Yellow
    Write-Host "   Make sure to check 'Add Python to PATH'" -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✓ Python found: $pythonCheck" -ForegroundColor Green
Write-Host ""

# Step 2: Install dependencies
Write-Host "2. Installing build dependencies..." -ForegroundColor Yellow
Write-Host "   Installing PyInstaller..." -ForegroundColor Gray
python -m pip install -q PyInstaller 2>&1 | Out-Null
Write-Host "   Installing yt-dlp..." -ForegroundColor Gray
python -m pip install -q yt-dlp 2>&1 | Out-Null
Write-Host "   ✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 3: Build
Write-Host "3. Building executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "   (This may take 2-5 minutes...)" -ForegroundColor Gray
Write-Host ""

python -m PyInstaller `
    --name=YouTubeVideoDownloader `
    --onefile `
    --windowed `
    --hidden-import=yt_dlp `
    --hidden-import=yt_dlp.extractor `
    --clean `
    --distpath=build_dist/dist `
    --workpath=build_dist/build `
    --specpath=build_dist `
    main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

# Step 4: Verify
$exePath = "build_dist/dist/YouTubeVideoDownloader.exe"
if (Test-Path $exePath) {
    $size = (Get-Item $exePath).Length / 1MB
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ SUCCESS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Executable created:" -ForegroundColor Cyan
    Write-Host "  Location: $(Resolve-Path $exePath)" -ForegroundColor White
    Write-Host "  Size: $([math]::Round($size, 1)) MB" -ForegroundColor White
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Test the executable by running it" -ForegroundColor White
    Write-Host "  2. (Optional) Create installer: .\create_installer.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✗ Executable not found!" -ForegroundColor Red
    exit 1
}
