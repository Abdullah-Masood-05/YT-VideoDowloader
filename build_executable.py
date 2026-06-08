"""
Build script for creating a standalone executable for YouTube Video Downloader
This script uses PyInstaller to bundle the application into a Windows executable.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'=' * 60}")
    print(f"📦 {description}")
    print(f"{'=' * 60}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - Command not found!")
        print(f"Make sure PyInstaller is installed: pip install pyinstaller")
        return False


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║   YouTube Video Downloader - Executable Builder            ║
╚════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Check dependencies
    print("\n1️⃣  Checking dependencies...")
    try:
        import PyInstaller

        print("   ✅ PyInstaller is installed")
    except ImportError:
        print("   ❌ PyInstaller not found. Installing...")
        if not run_command(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            "Install PyInstaller",
        ):
            return False

    try:
        import yt_dlp

        print("   ✅ yt-dlp is installed")
    except ImportError:
        print("   ⚠️  yt-dlp not found in current environment")

    # Step 2: Create build directory
    print("\n2️⃣  Setting up build directory...")
    build_dir = Path("build_dist")
    if build_dir.exists():
        print(f"   Removing existing {build_dir} directory...")
        shutil.rmtree(build_dir)

    # Step 3: Run PyInstaller
    print("\n3️⃣  Building executable with PyInstaller...")

    # PyInstaller command
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=YouTubeVideoDownloader",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--icon=app_icon.ico" if Path("app_icon.ico").exists() else "--nouptime",
        "--add-data=downloader_config.json:.",  # Include config file
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--clean",
        "--distpath=build_dist/dist",
        "--workpath=build_dist/build",
        "--specpath=build_dist",
        "main.py",
    ]

    # Remove the icon parameter if icon doesn't exist
    if not Path("app_icon.ico").exists():
        pyinstaller_cmd = [
            cmd
            for cmd in pyinstaller_cmd
            if cmd != "--icon=app_icon.ico" and cmd != "--nouptime"
        ]

    if not run_command(pyinstaller_cmd, "PyInstaller build"):
        return False

    # Step 4: Create installer (optional - requires NSIS)
    print("\n4️⃣  Build complete!")

    executable_path = Path("build_dist/dist/YouTubeVideoDownloader.exe")
    if executable_path.exists():
        print(f"\n{'=' * 60}")
        print("✅ SUCCESS! Executable created:")
        print(f"   📍 {executable_path.absolute()}")
        print(
            f"   📦 File size: {executable_path.stat().st_size / (1024 * 1024):.2f} MB"
        )
        print(f"{'=' * 60}")
        print("\n📋 Next steps:")
        print("   1. Test the executable by running it:")
        print(f"      {executable_path.absolute()}")
        print("   2. To create an installer (optional):")
        print("      - Install NSIS: https://nsis.sourceforge.io/")
        print("      - Run: create_installer.bat")
        return True
    else:
        print("❌ Executable not found after build!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
