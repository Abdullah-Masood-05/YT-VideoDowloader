# 🚀 Quick Start - Build Executable

## One-Line Solution for Windows

```bash
build.bat
```

That's it! Your executable will be ready in a few minutes.

---

## What You Get

✅ `YouTubeVideoDownloader.exe` - Standalone Windows app  
✅ Works on any Windows 7+ machine  
✅ No Python installation needed for end users  
✅ All dependencies bundled inside  

---

## Distribution

### Share the executable directly:
```
build_dist/dist/YouTubeVideoDownloader.exe
```

### Create an installer (optional):
```bash
create_installer.bat
```
Then share: `YouTubeVideoDownloader_Setup.exe`

---

## Before You Start

Make sure you have:

✅ **Python 3.8+** installed and in PATH  
✅ **FFmpeg** installed (users need this too)

Verify:
```bash
python --version
ffmpeg -version
```

Install FFmpeg (Windows):
```bash
winget install "FFmpeg (Essentials Build)"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Python not found | Install from python.org, check "Add Python to PATH" |
| PyInstaller not found | The build.bat installs it automatically |
| Build fails | Run: `pip install pyinstaller yt-dlp` |
| App won't start | Make sure FFmpeg is installed: `ffmpeg -version` |

---

## More Help

See `BUILD_GUIDE.md` for detailed instructions.
