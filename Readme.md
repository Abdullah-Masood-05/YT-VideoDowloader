# YouTube Video Downloader

A Windows desktop app for downloading YouTube videos, audio and thumbnails, built on
[yt-dlp](https://github.com/yt-dlp/yt-dlp) and PyQt6.

![Dark theme](docs/screenshots/dark.png)

## Features

- Quality list built from what each video actually offers (no fake 4K options)
- Video (MP4, optional H.264 for compatibility), audio (MP3, M4A, OPUS, WAV, FLAC) and thumbnail modes
- Embedded cover art and metadata
- Parallel downloads with progress, speed and ETA; download history
- Saves to your Downloads folder by default
- Dark theme by default, with a light theme switch

![Light theme](docs/screenshots/light.png)

## Install

Download `YouTubeVideoDownloader-Setup-<version>.exe` from
[Releases](https://github.com/Abdullah-Masood-05/YT-VideoDowloader/releases) and run it.
FFmpeg is bundled; nothing else is needed.

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12.

```sh
uv sync
uv run main.py
```

When running from source the app looks for `ffmpeg.exe` / `ffprobe.exe` in `ffmpeg\`,
then on `PATH`. The bundled binaries are a minimal LGPL build of FFmpeg 7.1.1
containing only what yt-dlp needs here (merging, audio conversion, thumbnail embedding).

## Building

Requires MSVC (Visual Studio Build Tools) and [Inno Setup 6](https://jrsoftware.org/isinfo.php).

```bat
uv sync
build.bat
```

This compiles a single-file exe with Nuitka into `build_dist\` and the installer into
`installer_output\`. Notes on the build flags are in `build.bat`.

## Project layout

```
main.py              main window
theme.py             dark / light themes
app_paths.py         paths for source and compiled builds
config_manager.py    settings in %APPDATA%\YouTubeVideoDownloader
download_manager.py  download queue
widgets/             UI components
workers/             fetch and download threads
resources/icons/     app icon
installer.iss        Inno Setup script
```

## License

FFmpeg is licensed under LGPL-2.1-or-later; the bundled build also links LAME (LGPL)
and libopus (BSD).
