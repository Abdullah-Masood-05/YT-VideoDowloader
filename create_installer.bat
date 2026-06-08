@echo off
REM YouTube Video Downloader - Create Installer
REM Requires NSIS to be installed: https://nsis.sourceforge.io/

echo.
echo Checking for NSIS installation...
echo.

REM Check if NSIS is installed
reg query "HKLM\Software\NSIS" >nul 2>&1
if errorlevel 1 (
    echo ❌ NSIS not found!
    echo.
    echo To create an installer, you need to install NSIS:
    echo https://nsis.sourceforge.io/
    echo.
    echo After installing NSIS, run this script again.
    pause
    exit /b 1
)

echo ✅ NSIS found!
echo.
echo Building installer...
echo.

makensis installer.nsi
if errorlevel 1 (
    echo ❌ Installer creation failed
    pause
    exit /b 1
)

echo.
echo ✅ Installer created successfully!
echo.
echo 📍 Installer location: YouTubeVideoDownloader_Setup.exe
echo.
pause
