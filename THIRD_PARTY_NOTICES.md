# Third-party notices

YouTube Video Downloader is licensed under the GNU General Public License v3.0 (see `LICENSE`).
It uses or ships the following components.

| Component | License | Source |
|---|---|---|
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) / Qt 6 | GPL-3.0 (PyQt6), LGPL-3.0 (Qt) | https://pypi.org/project/PyQt6/ |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | Unlicense | https://github.com/yt-dlp/yt-dlp |
| [requests](https://github.com/psf/requests) | Apache-2.0 | https://github.com/psf/requests |
| [FFmpeg](https://ffmpeg.org) 7.1.1 (minimal build, Windows/macOS packages) | LGPL-2.1-or-later | https://github.com/FFmpeg/FFmpeg/tree/n7.1.1 |
| [LAME](https://lame.sourceforge.io) (linked into FFmpeg) | LGPL-2.0-or-later | https://lame.sourceforge.io |
| [libopus](https://opus-codec.org) (linked into FFmpeg) | BSD-3-Clause | https://github.com/xiph/opus |

## FFmpeg build

The bundled `ffmpeg` / `ffprobe` are built from the unmodified FFmpeg `n7.1.1` tag with the
LGPL configuration in [`scripts/build_ffmpeg.sh`](scripts/build_ffmpeg.sh). Running that script
reproduces the binaries. `--enable-gpl` and `--enable-nonfree` are not used.

On Linux the packages use the distribution's own `ffmpeg` package instead.
