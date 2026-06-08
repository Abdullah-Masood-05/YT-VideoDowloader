@echo off
REM YouTube Video Downloader - Build Executable
REM This script builds the executable and optional installer

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   YouTube Video Downloader - Build Tool                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Step 1: Install dependencies
echo 1️⃣  Installing dependencies...
echo.
python -m pip install -q yt-dlp PyInstaller
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Step 2: Build executable
echo 2️⃣  Building executable...
echo.
python build_executable.py
if errorlevel 1 (
    echo ❌ Build failed
    pause
    exit /b 1
)

echo.
echo ✅ Build complete!
echo.
echo 📍 Executable location: build_dist\dist\YouTubeVideoDownloader.exe
echo.
pause
