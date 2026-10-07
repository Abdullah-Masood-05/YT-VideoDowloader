import yt_dlp
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class _QuietLogger:
    """Swallow yt-dlp output (stdout/stderr may be None in a windowed exe)."""

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class FetchWorker(QThread):
    info_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "logger": _QuietLogger(),
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)

            if info is None:
                self.error_occurred.emit("Could not extract video info.")
                return

            title = info.get("title") or "Unknown"
            channel = info.get("uploader") or info.get("channel") or "Unknown"
            duration = info.get("duration") or 0
            thumbnail_url = self._pick_thumbnail_url(info)
            description = info.get("description") or ""
            view_count = info.get("view_count") or 0
            upload_date = info.get("upload_date") or ""

            # QPixmap must only be created on the GUI thread; hand over a
            # QImage and let the widget convert it.
            thumbnail_image = self._fetch_thumbnail(thumbnail_url)

            formats = []
            seen = set()
            for f in info.get("formats") or []:
                fmt_id = f.get("format_id", "")
                ext = f.get("ext", "")
                vcodec = f.get("vcodec") or "none"
                acodec = f.get("acodec") or "none"
                height = f.get("height")
                fps = f.get("fps")
                filesize = f.get("filesize") or f.get("filesize_approx") or 0
                tbr = f.get("tbr") or 0
                abr = f.get("abr") or 0
                vbr = f.get("vbr") or 0

                has_video = vcodec != "none" and height
                has_audio = acodec != "none"

                if has_video and has_audio:
                    fmt_type = "video+audio"
                elif has_video:
                    fmt_type = "video-only"
                elif has_audio:
                    fmt_type = "audio-only"
                else:
                    continue

                key = f"{height or 0}_{fps or 0}_{ext}_{fmt_type}"
                if key in seen:
                    continue
                seen.add(key)

                resolution = f"{height}p" if height else "N/A"
                fps_str = f"{int(fps)}" if fps else "N/A"
                size_str = self._format_size(filesize)

                formats.append({
                    "format_id": fmt_id,
                    "ext": ext,
                    "resolution": resolution,
                    "height": height or 0,
                    "fps": fps_str,
                    "vcodec": vcodec if vcodec != "none" else "-",
                    "acodec": acodec if acodec != "none" else "-",
                    "filesize": filesize,
                    "filesize_str": size_str,
                    "tbr": tbr,
                    "abr": abr,
                    "vbr": vbr,
                    "fmt_type": fmt_type,
                })

            formats.sort(key=lambda x: (-x["height"], -x["tbr"]))

            qualities = self._collect_qualities(info)

            duration_str = self._format_duration(duration)
            views_str = f"{view_count:,}" if view_count else "N/A"

            result = {
                "title": title,
                "channel": channel,
                "duration": duration_str,
                "duration_seconds": duration,
                "thumbnail_image": thumbnail_image,
                "thumbnail_url": thumbnail_url,
                "description": description[:300],
                "view_count": views_str,
                "upload_date": upload_date,
                "formats": formats,
                "qualities": qualities,
                "is_playlist": bool(info.get("entries")),
                "url": self.url,
            }

            self.info_ready.emit(result)

        except Exception as e:
            error_msg = str(e)
            if "ERROR" in error_msg:
                error_msg = error_msg.split("ERROR:")[-1].strip()
            self.error_occurred.emit(error_msg)

    @staticmethod
    def _collect_qualities(info):
        """Build the list of video heights actually available.

        Returns a list of dicts sorted by height descending:
        {"height": int, "fps": int, "filesize": int}. For playlists the
        heights of all entries are merged (union); size is omitted there.
        """
        entries = info.get("entries")
        if entries:
            sources = [e for e in entries if isinstance(e, dict)]
            is_playlist = True
        else:
            sources = [info]
            is_playlist = False

        by_height = {}
        for src in sources:
            src_formats = src.get("formats") or []

            best_audio_size = 0
            for f in src_formats:
                if f.get("acodec", "none") != "none" and f.get("vcodec", "none") == "none":
                    size = f.get("filesize") or f.get("filesize_approx") or 0
                    best_audio_size = max(best_audio_size, size)

            for f in src_formats:
                height = f.get("height")
                if f.get("vcodec", "none") == "none" or not height:
                    continue

                fps = int(f.get("fps") or 0)
                size = f.get("filesize") or f.get("filesize_approx") or 0
                if size and f.get("acodec", "none") == "none":
                    size += best_audio_size

                entry = by_height.setdefault(height, {"height": height, "fps": 0, "filesize": 0})
                entry["fps"] = max(entry["fps"], fps)
                if not is_playlist:
                    entry["filesize"] = max(entry["filesize"], size)

        return sorted(by_height.values(), key=lambda q: -q["height"])

    @staticmethod
    def _pick_thumbnail_url(info):
        url = info.get("thumbnail")
        if url:
            return url
        thumbs = [t for t in (info.get("thumbnails") or []) if t.get("url")]
        if thumbs:
            return thumbs[-1]["url"]
        for entry in info.get("entries") or []:
            if isinstance(entry, dict):
                url = entry.get("thumbnail")
                if url:
                    return url
        return ""

    def _fetch_thumbnail(self, url):
        """Download the thumbnail and return it as a QImage (thread-safe)."""
        if not url:
            return QImage()
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            image = QImage()
            if not image.loadFromData(resp.content):
                # WebP may be unsupported by the bundled image plugins; try
                # YouTube's JPEG variant of the same thumbnail.
                if "/vi_webp/" in url:
                    jpg_url = url.replace("/vi_webp/", "/vi/").rsplit(".", 1)[0] + ".jpg"
                    resp = requests.get(jpg_url, timeout=10)
                    resp.raise_for_status()
                    image.loadFromData(resp.content)
            return image
        except Exception:
            return QImage()

    @staticmethod
    def _format_size(size_bytes):
        if not size_bytes:
            return "N/A"
        units = ["B", "KB", "MB", "GB"]
        size = float(size_bytes)
        for unit in units:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def _format_duration(seconds):
        if not seconds:
            return "0:00"
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
