#!/usr/bin/env bash
# Build "YouTube Video Downloader.app" with Nuitka (standalone app bundle),
# bundle ffmpeg/ffprobe next to the main binary and ad-hoc sign the bundle.
#
# Run from the repository root after `uv sync --locked`:
#   packaging/macos/build_app.sh <version> [ffmpeg-dir]
# Output: build_macos/YouTube Video Downloader.app
set -euo pipefail

VERSION="${1:?usage: build_app.sh <version> [ffmpeg-dir]}"
FFMPEG_DIR="${2:-ffmpeg}"
APP_NAME="YouTube Video Downloader"
BUNDLE_ID="com.abdullahmasood.ytdownloader"
BIN_NAME="YouTubeVideoDownloader"
OUT="build_macos"
ICNS="$OUT/app.icns"
PYTHON="${PYTHON:-.venv/bin/python}"

mkdir -p "$OUT"
[ -f "$ICNS" ] || packaging/macos/make_icns.sh resources/icons/app_source.png "$ICNS"

rm -rf "$OUT"/*.app "$OUT"/*.dist "$OUT"/*.build

# --mode=app-dist: standalone folder wrapped in an .app bundle (not onefile),
# so files placed in Contents/MacOS are next to the binary and found by
# app_paths.find_ffmpeg() via sys.argv[0].
"$PYTHON" -m nuitka \
  --mode=app-dist \
  --lto=no \
  --jobs="$(sysctl -n hw.ncpu)" \
  --enable-plugin=pyqt6 \
  --noinclude-custom-mode=yt_dlp.extractor:bytecode \
  --nofollow-import-to=unittest,test,pytest,_pytest,doctest,pdb \
  --nofollow-import-to=setuptools,pip,distutils,pkg_resources \
  --noinclude-setuptools-mode=nofollow \
  --python-flag=no_docstrings \
  --include-qt-plugins=sensible,styles,platforms \
  --include-data-files=resources/icons/app.png=resources/icons/app.png \
  --macos-app-icon="$ICNS" \
  --macos-app-name="$APP_NAME" \
  --macos-signed-app-name="$BUNDLE_ID" \
  --macos-app-version="$VERSION" \
  --macos-app-mode=gui \
  --product-name="$APP_NAME" \
  --product-version="$VERSION" \
  --copyright="Copyright (c) 2026 Abdullah Masood. GPL-3.0." \
  --assume-yes-for-downloads \
  --output-filename="$BIN_NAME" \
  --output-dir="$OUT" \
  --remove-output \
  main.py

BUILT_APP="$(find "$OUT" -maxdepth 1 -name '*.app' -type d | head -n 1)"
[ -n "$BUILT_APP" ] || { echo "ERROR: no .app produced in $OUT" >&2; ls -la "$OUT"; exit 1; }
APP="$OUT/$APP_NAME.app"
if [ "$BUILT_APP" != "$APP" ]; then
  mv "$BUILT_APP" "$APP"
fi

MACOS_DIR="$APP/Contents/MacOS"
EXE="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$APP/Contents/Info.plist")"
[ -x "$MACOS_DIR/$EXE" ] || { echo "ERROR: main binary $MACOS_DIR/$EXE missing" >&2; exit 1; }

# Bundle ffmpeg + ffprobe next to the main binary.
for tool in ffmpeg ffprobe; do
  if [ -f "$FFMPEG_DIR/$tool" ]; then
    cp "$FFMPEG_DIR/$tool" "$MACOS_DIR/$tool"
    chmod 755 "$MACOS_DIR/$tool"
  else
    echo "WARNING: $FFMPEG_DIR/$tool not found; app will be built without it." >&2
  fi
done

# Re-seal the bundle (adding ffmpeg invalidated Nuitka's ad-hoc signature).
xattr -cr "$APP"
codesign --force --deep -s - "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"

echo ">> built $APP"
/usr/libexec/PlistBuddy -c 'Print' "$APP/Contents/Info.plist"
du -sh "$APP"
