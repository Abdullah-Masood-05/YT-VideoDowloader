#!/usr/bin/env python
"""
Simple build script for YouTube Video Downloader
Run directly: python build_simple.py
"""

import os
import subprocess
import sys
from pathlib import Path


def main():
    print("\n" + "=" * 60)
    print("YouTube Video Downloader - Build Executable")
    print("=" * 60 + "\n")

    # Step 1: Install dependencies
    print("1. Installing build dependencies...")
    deps = ["pyinstaller", "yt-dlp"]
    for dep in deps:
        print(f"   Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", dep])

    print("   ✓ Dependencies installed\n")

    # Step 2: Build with PyInstaller
    print("2. Building executable with PyInstaller...")
    print("   (This may take 2-5 minutes...)\n")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=YouTubeVideoDownloader",
        "--onefile",
        "--windowed",
        "--hidden-import=yt_dlp",
        "--hidden-import=yt_dlp.extractor",
        "--clean",
        "--distpath=build_dist/dist",
        "--workpath=build_dist/build",
        "--specpath=build_dist",
        "main.py",
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\n✗ Build failed!")
        return False

    # Step 3: Verify
    exe_path = Path("build_dist/dist/YouTubeVideoDownloader.exe")
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print("\n" + "=" * 60)
        print("✓ SUCCESS!")
        print("=" * 60)
        print(f"\nExecutable created:")
        print(f"  Location: {exe_path.absolute()}")
        print(f"  Size: {size_mb:.1f} MB\n")
        print("Next steps:")
        print("  1. Test the executable")
        print("  2. (Optional) Create installer: python create_installer_simple.py")
        return True
    else:
        print("\n✗ Executable not found!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
