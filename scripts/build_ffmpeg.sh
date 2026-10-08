#!/usr/bin/env bash
# Build the minimal, LGPL, statically linked ffmpeg + ffprobe bundled with
# YouTube Video Downloader.
#
# Vendored from the ffmpeg-ytdl-minimal-build project. The configure flags
# below are identical to that build; only the paths were made configurable.
#
# The build contains exactly what yt-dlp's post-processors need:
#   - merging bestvideo+bestaudio into mp4/mkv/webm (stream copy)
#   - extracting audio to mp3 / m4a / opus / wav / flac (+ vorbis, aac)
#   - converting / embedding thumbnails (webp -> png/jpg, attached_pic)
#   - metadata / chapter embedding and the usual container fixups
#
# What this does:
#   1. Clones FFmpeg at the n7.1.1 tag (shallow)
#   2. Configures it from --disable-all, re-enabling only the pieces above
#   3. Builds ffmpeg and ffprobe (static on Windows, no DLLs)
#   4. Copies the results to the output directory
#
# Requirements on Windows (MSYS2 MINGW64 shell):
#   pacman -S --needed git make diffutils \
#     mingw-w64-x86_64-gcc mingw-w64-x86_64-nasm mingw-w64-x86_64-pkgconf \
#     mingw-w64-x86_64-lame mingw-w64-x86_64-opus mingw-w64-x86_64-zlib
#
# On other platforms (for example macOS) you need a C compiler, make, nasm,
# pkg-config, lame, opus and zlib. The Windows-only cross/static flags are
# skipped there; the feature set is the same.
#
# Note: FFmpeg's configure does not like spaces in the build path. The source
# dir defaults to a temp location; override it with FFMPEG_SRC_DIR.
#
# Usage:
#   scripts/build_ffmpeg.sh [output-dir]       (default: ./ffmpeg)
#
# Environment:
#   FFMPEG_SRC_DIR  where to clone/build FFmpeg (default: $TMPDIR/ffmpeg-n7.1.1-src)
#   JOBS            parallel make jobs (default: number of CPUs)
set -euo pipefail

FFMPEG_TAG="n7.1.1"
UPSTREAM_URL="https://github.com/FFmpeg/FFmpeg.git"
OUT_DIR="${1:-ffmpeg}"
SRC_DIR="${FFMPEG_SRC_DIR:-${TMPDIR:-/tmp}/ffmpeg-${FFMPEG_TAG}-src}"

mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) IS_WINDOWS=1; EXE=".exe" ;;
  *)                    IS_WINDOWS=0; EXE="" ;;
esac

if [ -z "${JOBS:-}" ]; then
  JOBS="$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)"
fi

# ── 1. Source ──────────────────────────────────────────────────────────────
if [ ! -d "$SRC_DIR/.git" ]; then
  echo ">> cloning FFmpeg ${FFMPEG_TAG} into $SRC_DIR"
  git clone --depth 1 --branch "$FFMPEG_TAG" "$UPSTREAM_URL" "$SRC_DIR"
fi
cd "$SRC_DIR"
git checkout --force "$FFMPEG_TAG" >/dev/null 2>&1 || true

# ── 2. Configure ───────────────────────────────────────────────────────────
# Containers yt-dlp reads from YouTube (and most other sites) and writes to.
DEMUXERS="mov,matroska,aac,mp3,ogg,flac,wav,mpegts,concat,ffmetadata,image2,image_png_pipe,image_jpeg_pipe,image_webp_pipe"
# mp4/ipod(m4a)/mov, matroska/webm, audio outputs, adts (aac), image2 (thumbs)
MUXERS="mp4,ipod,mov,matroska,webm,mp3,ogg,opus,flac,wav,adts,image2,null"
# Audio decoders: everything a source audio track may be, so it can be
# re-encoded. Image decoders: thumbnail conversion (webp needs vp8 internally).
# vp9: never used to transcode, but stream-info probing needs it to learn the
# pixel format / bit depth of VP9 tracks from webm. Without it the mp4 muxer
# writes an empty vpcC box and the merged VP9 .mp4 cannot be read back.
DECODERS="aac,mp3float,opus,vorbis,flac,pcm_s16le,pcm_s24le,pcm_f32le,png,mjpeg,webp,vp9"
# libmp3lame -> mp3, aac (native) -> m4a, libopus -> opus, flac, pcm -> wav,
# png/mjpeg -> thumbnail conversion.
ENCODERS="libmp3lame,aac,libopus,flac,pcm_s16le,png,mjpeg"
# Parsers make stream-copy remuxing reliable (keyframes, extradata, timing).
PARSERS="aac,h264,hevc,vp8,vp9,av1,opus,vorbis,mpegaudio,flac,png,mjpeg,webp"
# Bitstream filters the mp4/mkv muxers insert automatically or yt-dlp asks for.
BSFS="aac_adtstoasc,h264_mp4toannexb,hevc_mp4toannexb,vp9_superframe,vp9_superframe_split,av1_frame_merge,av1_frame_split,extract_extradata,setts,mjpeg2jpeg,null"
# Filters ffmpeg's CLI auto-inserts for audio/pixel-format conversion.
FILTERS="aresample,aformat,anull,atrim,format,null,trim,scale,copy,acopy"

PLATFORM_FLAGS=()
if [ "$IS_WINDOWS" = 1 ]; then
  PLATFORM_FLAGS=(
    --enable-cross-compile
    --arch=x86_64
    --target-os=mingw32
    --extra-ldflags="-static -static-libgcc"
  )
fi

echo ">> configuring minimal build"
./configure \
  --disable-all \
  ${PLATFORM_FLAGS[@]+"${PLATFORM_FLAGS[@]}"} \
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
  --pkg-config-flags=--static

# ── 3. Build ───────────────────────────────────────────────────────────────
echo ">> building with $JOBS jobs (this takes a while)"
make -j"$JOBS" "ffmpeg$EXE" "ffprobe$EXE"
strip "ffmpeg$EXE" "ffprobe$EXE"

# ── 4. Extract ─────────────────────────────────────────────────────────────
cp "ffmpeg$EXE" "ffprobe$EXE" "$OUT_DIR/"
echo ">> done:"
ls -l "$OUT_DIR/ffmpeg$EXE" "$OUT_DIR/ffprobe$EXE"
if [ "$IS_WINDOWS" = 1 ]; then
  echo ">> runtime DLL imports (should be Windows system DLLs only):"
  objdump -p "$OUT_DIR/ffmpeg$EXE" | grep "DLL Name" || true
fi
