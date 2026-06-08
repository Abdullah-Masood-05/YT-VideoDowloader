# Build Your Desktop App - PowerShell Edition

Since you're using PowerShell 7.6, here are the commands to build your executable:

## Quick Start

### Option 1: Using PowerShell Script (Recommended)
```powershell
.\build.ps1
```

### Option 2: Using Python Script
```powershell
python build_simple.py
```

### Option 3: Manual Build
```powershell
# Install dependencies
pip install pyinstaller yt-dlp

# Build executable
python -m PyInstaller `
    --name=YouTubeVideoDownloader `
    --onefile `
    --windowed `
    --hidden-import=yt_dlp `
    --hidden-import=yt_dlp.extractor `
    --clean `
    --distpath=build_dist/dist `
    --buildpath=build_dist/build `
    --specpath=build_dist `
    main.py
```

## Important Note About PowerShell

If you get an execution policy error, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try: `.\build.ps1`

## Expected Output

After running, you should see:
- Dependencies being installed
- PyInstaller working (2-5 minutes)
- Success message with executable location
- Executable at: `build_dist/dist/YouTubeVideoDownloader.exe`

## Troubleshooting

**Error: "Python not found"**
- Reinstall Python from python.org
- Make sure "Add Python to PATH" is checked
- Restart PowerShell

**Error: "PyInstaller not found"**
- The build script installs it automatically
- Or run: `pip install pyinstaller`

**Build fails**
- Run: `pip install --upgrade pyinstaller yt-dlp`
- Try the manual build option above

## Your venv Activation Note

You're using `/venv/bin/activate` which is correct for your Unix-like venv structure.
When running the build scripts, the Python from your venv will be used automatically.

---

**Choose an option above and run it now!**
