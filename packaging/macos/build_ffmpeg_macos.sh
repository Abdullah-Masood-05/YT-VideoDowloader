#!/usr/bin/env bash
# Build a minimal, LGPL FFmpeg (ffmpeg + ffprobe) for macOS (native arch).
#
# Same configuration as the Windows ffmpeg-ytdl-minimal-build (FFmpeg n7.1.1,
# --disable-all plus only what yt-dlp's post-processors need), adapted for
# darwin. libmp3lame and libopus are linked statically from Homebrew's .a
# archives, so the resulting binaries depend only on system libraries
# (/usr/lib/libSystem, /usr/lib/libz).
#
# Requirements: Xcode command line tools, Homebrew: brew install lame opus pkgconf
#
# Usage: packaging/macos/build_ffmpeg_macos.sh [out-dir]
#   Env: WORK_DIR (default: $RUNNER_TEMP or /tmp)/ffmpeg-macos-build
#        MACOSX_DEPLOYMENT_TARGET (default 11.0)
set -euo pipefail

FFMPEG_TAG="n7.1.1"
UPSTREAM_URL="https://github.com/FFmpeg/FFmpeg.git"
OUT_DIR="$(mkdir -p "${1:-ffmpeg}" && cd "${1:-ffmpeg}" && pwd)"
WORK_DIR="${WORK_DIR:-${RUNNER_TEMP:-/tmp}/ffmpeg-macos-build}"
SRC_DIR="$WORK_DIR/ffmpeg-src"
DEPS_DIR="$WORK_DIR/deps"
export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-11.0}"

case "$WORK_DIR" in
  *" "*) echo "ERROR: FFmpeg's configure does not support spaces in WORK_DIR ($WORK_DIR)" >&2; exit 1 ;;
esac

# ── 1. Static libmp3lame / libopus from Homebrew ───────────────────────────
# Copy only the .a archives into a private lib dir so the linker can never
# pick up the Homebrew .dylibs.
LAME_PREFIX="$(brew --prefix lame)"
OPUS_PREFIX="$(brew --prefix opus)"
for f in "$LAME_PREFIX/lib/libmp3lame.a" "$OPUS_PREFIX/lib/libopus.a" \
         "$LAME_PREFIX/include/lame/lame.h" "$OPUS_PREFIX/include/opus/opus.h"; do
  [ -f "$f" ] || { echo "ERROR: missing $f (brew install lame opus)" >&2; exit 1; }
done
rm -rf "$DEPS_DIR"
mkdir -p "$DEPS_DIR/lib/pkgconfig" "$DEPS_DIR/include"
cp "$LAME_PREFIX/lib/libmp3lame.a" "$OPUS_PREFIX/lib/libopus.a" "$DEPS_DIR/lib/"
cp -R "$LAME_PREFIX/include/lame" "$DEPS_DIR/include/"
cp -R "$OPUS_PREFIX/include/opus" "$DEPS_DIR/include/"
cat > "$DEPS_DIR/lib/pkgconfig/opus.pc" <<EOF
prefix=$DEPS_DIR
libdir=\${prefix}/lib
includedir=\${prefix}/include

Name: Opus
Description: Opus IETF audio codec (static)
Version: $(pkg-config --modversion "$OPUS_PREFIX/lib/pkgconfig/opus.pc" 2>/dev/null || echo 1.5)
Libs: -L\${libdir} -lopus
Libs.private: -lm
Cflags: -I\${includedir}/opus
EOF
# Only our own .pc files are visible to configure.
export PKG_CONFIG_LIBDIR="$DEPS_DIR/lib/pkgconfig"
unset PKG_CONFIG_PATH

# ── 2. Source ──────────────────────────────────────────────────────────────
if [ ! -d "$SRC_DIR/.git" ]; then
  echo ">> cloning FFmpeg ${FFMPEG_TAG}"
  git clone --depth 1 --branch "$FFMPEG_TAG" "$UPSTREAM_URL" "$SRC_DIR"
fi
cd "$SRC_DIR"
git checkout --force "$FFMPEG_TAG" >/dev/null 2>&1 || true

# ── 3. Configure (identical component lists to the Windows build) ──────────
DEMUXERS="mov,matroska,aac,mp3,ogg,flac,wav,mpegts,concat,ffmetadata,image2,image_png_pipe,image_jpeg_pipe,image_webp_pipe"
MUXERS="mp4,ipod,mov,matroska,webm,mp3,ogg,opus,flac,wav,adts,image2,null"
DECODERS="aac,mp3float,opus,vorbis,flac,pcm_s16le,pcm_s24le,pcm_f32le,png,mjpeg,webp,vp9"
ENCODERS="libmp3lame,aac,libopus,flac,pcm_s16le,png,mjpeg"
PARSERS="aac,h264,hevc,vp8,vp9,av1,opus,vorbis,mpegaudio,flac,png,mjpeg,webp"
BSFS="aac_adtstoasc,h264_mp4toannexb,hevc_mp4toannexb,vp9_superframe,vp9_superframe_split,av1_frame_merge,av1_frame_split,extract_extradata,setts,mjpeg2jpeg,null"
FILTERS="aresample,aformat,anull,atrim,format,null,trim,scale,copy,acopy"

echo ">> configuring minimal build (target macOS $MACOSX_DEPLOYMENT_TARGET, $(uname -m))"
./configure \
  --disable-all \
  --target-os=darwin \
  --enable-ffmpeg \
  --enable-ffprobe \
  --enable-avcodec \
  --enable-avformat \
  --enable-avutil \
  --enable-avfilter \
  --enable-swresample \
  --enable-swscale \
  --enable-protocol=file,pipe \
  --enable-demuxer="$DEMUXERS" \
  --enable-muxer="$MUXERS" \
  --enable-decoder="$DECODERS" \
  --enable-encoder="$ENCODERS" \
  --enable-parser="$PARSERS" \
  --enable-bsf="$BSFS" \
  --enable-filter="$FILTERS" \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-zlib \
  --disable-autodetect \
  --enable-small \
  --disable-doc \
  --disable-ffplay \
  --disable-network \
  --disable-debug \
  --pkg-config=pkg-config \
  --pkg-config-flags=--static \
  --extra-cflags="-I$DEPS_DIR/include -mmacosx-version-min=$MACOSX_DEPLOYMENT_TARGET" \
  --extra-ldflags="-L$DEPS_DIR/lib -mmacosx-version-min=$MACOSX_DEPLOYMENT_TARGET"

# ── 4. Build ───────────────────────────────────────────────────────────────
echo ">> building"
make -j"$(sysctl -n hw.ncpu)" ffmpeg ffprobe
strip ffmpeg ffprobe
# strip invalidates the linker's ad-hoc signature; re-sign (required on arm64).
codesign --force -s - ffmpeg ffprobe

# ── 5. Install + verify ────────────────────────────────────────────────────
cp ffmpeg ffprobe "$OUT_DIR/"
echo ">> done:"
ls -l "$OUT_DIR/ffmpeg" "$OUT_DIR/ffprobe"

echo ">> dynamic library dependencies (must be system libs only):"
status=0
for bin in "$OUT_DIR/ffmpeg" "$OUT_DIR/ffprobe"; do
  otool -L "$bin"
  bad="$(otool -L "$bin" | tail -n +2 | awk '{print $1}' | grep -Ev '^(/usr/lib/|/System/)' || true)"
  if [ -n "$bad" ]; then
    echo "ERROR: $bin links non-system libraries:" >&2
    echo "$bad" >&2
    status=1
  fi
done
"$OUT_DIR/ffmpeg" -hide_banner -version | sed -n 1,3p
exit $status
