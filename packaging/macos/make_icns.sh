#!/usr/bin/env bash
# Generate app.icns from a square PNG using the macOS built-in sips + iconutil.
#
# Usage: packaging/macos/make_icns.sh [source.png] [output.icns]
set -euo pipefail

SRC="${1:-resources/icons/app_source.png}"
OUT="${2:-build_macos/app.icns}"

if [ ! -f "$SRC" ]; then
  echo "ERROR: source image not found: $SRC" >&2
  exit 1
fi

WORK="$(mktemp -d)"
ICONSET="$WORK/app.iconset"
mkdir -p "$ICONSET" "$(dirname "$OUT")"

for size in 16 32 128 256 512; do
  double=$((size * 2))
  sips -s format png -z "$size" "$size" "$SRC" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
  sips -s format png -z "$double" "$double" "$SRC" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done

iconutil -c icns "$ICONSET" -o "$OUT"
rm -rf "$WORK"
echo ">> wrote $OUT"
ls -l "$OUT"
