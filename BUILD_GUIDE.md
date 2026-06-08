# 🎬 YouTube Video Downloader - Build Guide

This guide explains how to create a standalone executable desktop app from the YouTube Video Downloader project.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Building the Executable](#building-the-executable)
4. [Creating an Installer](#creating-an-installer)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

**Windows users:** Run the build script to create an executable in ~2-5 minutes:

```bash
build.bat
```

This will automatically:
1. ✅ Install dependencies
2. ✅ Build the executable
3. ✅ Show you the location of the executable

---

## ✅ Prerequisites

### Required

1. **Python 3.8+** - [Download](https://www.python.org/)
   - Make sure to check "Add Python to PATH" during installation
   
2. **FFmpeg** - Required for video processing
   - **Windows (Winget):**
     ```bash
     winget install "FFmpeg (Essentials Build)"
     ```
   - **Windows (Chocolatey):**
     ```bash
     choco install ffmpeg
     ```
   - **macOS:**
     ```bash
     brew install ffmpeg
     ```
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt install ffmpeg
     ```

### Verify Installation

```bash
python --version
ffmpeg -version
```

---

## 🔨 Building the Executable

### Method 1: Using the Build Script (Recommended for Windows)

```bash
build.bat
```

The script will:
- Install required Python packages (yt-dlp, PyInstaller)
- Create a standalone executable
- Display the executable location

### Method 2: Manual Build

**Step 1: Install build dependencies**

```bash
pip install pyinstaller yt-dlp
```

**Step 2: Run the build script**

```bash
python build_executable.py
```

**Step 3: Find your executable**

The executable will be located at:
```
build_dist/dist/YouTubeVideoDownloader.exe
```

### What Gets Bundled

✅ All Python dependencies (yt-dlp)  
✅ The Tkinter GUI framework (included with Python)  
✅ Config files  
✅ All source modules  

**Note:** FFmpeg is NOT bundled - users need to install it separately (see Prerequisites above)

---

## 📦 Creating an Installer (Optional)

If you want to distribute your app with an installer, follow these steps:

### Prerequisites for Installer

1. **NSIS** (Nullsoft Scriptable Install System)
   - Download: [https://nsis.sourceforge.io/](https://nsis.sourceforge.io/)
   - Run the installer with default settings

### Build the Installer

**Step 1:** Build the executable first (see above)

**Step 2:** Run the installer creation script

```bash
create_installer.bat
```

Or manually:

```bash
makensis installer.nsi
```

**Step 3:** Find your installer

```
YouTubeVideoDownloader_Setup.exe
```

### What the Installer Does

✅ Installs to `Program Files\YouTube Video Downloader`  
✅ Creates Start Menu shortcuts  
✅ Creates Desktop shortcut (optional)  
✅ Adds Uninstall option to Control Panel  
✅ Registers in Windows Registry  

---

## 🧪 Testing Your Build

### Test the Executable

1. Navigate to `build_dist/dist/`
2. Double-click `YouTubeVideoDownloader.exe`
3. The app should launch with the GUI

### Test the Installer

1. Run `YouTubeVideoDownloader_Setup.exe`
2. Follow the installation wizard
3. Launch from Start Menu or Desktop shortcut

### Troubleshooting Common Issues

See [Troubleshooting](#troubleshooting) section below

---

## 🐛 Troubleshooting

### Error: "Python is not installed or not in PATH"

**Solution:**
- Install Python from [https://www.python.org/](https://www.python.org/)
- **Important:** Check "Add Python to PATH" during installation
- Restart your terminal/command prompt

### Error: "PyInstaller not found"

**Solution:**
```bash
pip install pyinstaller
```

### Error: "FFmpeg not found" when running app

**Solution:**
- Install FFmpeg (see Prerequisites section)
- The application needs FFmpeg to merge video/audio streams
- Users will see an error message if FFmpeg is missing

### Executable is very large (200+ MB)

**Note:** This is normal! PyInstaller bundles:
- Python runtime (~80+ MB)
- yt-dlp and dependencies
- Tkinter libraries

To reduce size, you can use `--onedir` instead of `--onefile` in the build script (creates a folder instead of single file).

### App crashes on startup

**Check:**
1. Python version is 3.8+: `python --version`
2. All dependencies installed: `pip install -r requirements.txt`
3. Config file exists: `downloader_config.json` in the project directory
4. FFmpeg is installed: `ffmpeg -version`

### "Could not find yt-dlp module"

**Solution:**
Make sure you're building from the correct environment:
```bash
pip install yt-dlp
python build_executable.py
```

---

## 📁 Project Structure After Build

```
YT-VideoDowloader/
├── main.py                          # Main application
├── config_manager.py                # Configuration handler
├── download_manager.py              # Download handler
├── Downloader.py                    # Legacy downloader
├── requirements.txt                 # Python dependencies
├── build_executable.py              # Build script (Python)
├── build.bat                        # Build script (Windows)
├── installer.nsi                    # NSIS installer config
├── create_installer.bat             # Installer creation script
├── downloader_config.json           # Configuration file
├── download_history.log             # Download history
│
└── build_dist/                      # Generated during build
    ├── dist/
    │   └── YouTubeVideoDownloader.exe   # Final executable ✅
    ├── build/                           # Build artifacts
    └── YouTubeVideoDownloader.spec      # PyInstaller spec file
```

---

## 📝 Distribution

### Distributing the Executable Alone

Simply share `build_dist/dist/YouTubeVideoDownloader.exe` with users.

**Users must have:**
- Windows 7 or later
- FFmpeg installed (or bundled)

### Distributing with Installer

Share `YouTubeVideoDownloader_Setup.exe`

The installer makes it easier for end users:
- Handles installation automatically
- Creates shortcuts
- Adds uninstall support

---

## 🔄 Updating the App

When you make changes:

1. Test locally with `python main.py`
2. Rebuild with `build.bat`
3. Test the new executable
4. Rebuild installer if distributing

---

## 🎯 Advanced Options

### Custom Icon

1. Create or download a `.ico` file (e.g., `app_icon.ico`)
2. Place it in the project root
3. The build script will automatically detect and use it

### Customizing the Installer

Edit `installer.nsi` to change:
- Product name and version
- Publisher name
- Website URL
- Installation directory
- Shortcuts and file associations

---

## ⚖️ License & Distribution

Make sure you have the right to distribute your app with:
- ✅ yt-dlp (UNLICENSE)
- ✅ Python (PSF License)
- ✅ Your own code (choose your license)

---

## 📞 Support

For issues with:

- **yt-dlp:** [GitHub Issues](https://github.com/yt-dlp/yt-dlp/issues)
- **PyInstaller:** [Documentation](https://pyinstaller.org/)
- **FFmpeg:** [Official Docs](https://ffmpeg.org/documentation.html)

---

**Happy building! 🚀**
