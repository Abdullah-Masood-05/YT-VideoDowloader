#!/usr/bin/env bash
# Build the Linux standalone app with Nuitka and stage everything nfpm needs.
#
# Run from the repository root after `uv sync --locked`:
#   packaging/linux/build.sh
#
# Output (all under build/linux/):
#   dist/                      Nuitka standalone folder -> /opt/youtube-video-downloader
#   icons/<N>x<N>/apps/*.png   hicolor icons
set -euo pipefail

cd "$(dirname "$0")/../.."

APP=youtube-video-downloader
OUT=build/linux
PYTHON=${PYTHON:-.venv/bin/python}

rm -rf "$OUT"
mkdir -p "$OUT"

# Same trimming flags as build.bat (see docs/NUITKA_BUILD_NOTES.md), but
# --standalone: the packages install a folder, so there is no onefile
# extraction step at every launch.
"$PYTHON" -m nuitka \
    --standalone \
    --lto=no \
    --jobs="$(nproc)" \
    --enable-plugin=pyqt6 \
    --noinclude-custom-mode=yt_dlp.extractor:bytecode \
    --nofollow-import-to=unittest,test,pytest,_pytest,doctest,pdb \
    --nofollow-import-to=setuptools,pip,distutils,pkg_resources \
    --noinclude-setuptools-mode=nofollow \
    --python-flag=no_docstrings \
    --include-qt-plugins=sensible,styles,platforms,xcbglintegrations \
    --include-data-files=resources/icons/app.png=resources/icons/app.png \
    --include-data-files=resources/icons/app.ico=resources/icons/app.ico \
    --assume-yes-for-downloads \
    --output-filename="$APP" \
    --output-dir="$OUT/nuitka" \
    --remove-output \
    main.py

mv "$OUT/nuitka/main.dist" "$OUT/dist"
rm -rf "$OUT/nuitka"
test -x "$OUT/dist/$APP"

"$PYTHON" packaging/linux/make_icons.py resources/icons/app_source.png "$OUT/icons"

echo "Staged in $OUT:"
du -sh "$OUT/dist"
