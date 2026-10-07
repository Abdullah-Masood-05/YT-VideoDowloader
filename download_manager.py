import os
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal

import config_manager
from workers.download_worker import DownloadWorker


class DownloadManager(QObject):
    """Runs DownloadWorkers, at most ``max_concurrent`` at a time.

    All methods are called on the GUI thread; worker signals are delivered
    here via queued connections, so no extra locking is needed.
    """

    download_added = pyqtSignal(int, str)
    download_started = pyqtSignal(int)
    download_progress = pyqtSignal(int, str, str, str, str)
    download_status = pyqtSignal(int, str)
    download_complete = pyqtSignal(int, str, str)
    download_error = pyqtSignal(int, str)
    download_cancelled = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers = {}   # dl_id -> info dict (queued or running)
        self._queue = []     # dl_ids waiting to start
        self._next_id = 0
        self._max_concurrent = 3
        self._history_file = config_manager.HISTORY_FILE

    def set_max_concurrent(self, n):
        self._max_concurrent = max(1, int(n))
        self._start_queued()

    def has_pending(self):
        return bool(self._workers)

    def add_download(self, url, options, title="Unknown"):
        self._next_id += 1
        dl_id = self._next_id

        # Parent the worker to the manager so Python's GC can never destroy
        # a QThread that is still running.
        worker = DownloadWorker(url, options, dl_id, self)
        worker.progress_updated.connect(
            lambda p, s, e, z, i=dl_id: self.download_progress.emit(i, p, s, e, z)
        )
        worker.status_updated.connect(
            lambda s, i=dl_id: self.download_status.emit(i, s)
        )
        worker.download_complete.connect(
            lambda t, path, i=dl_id: self._on_complete(i, t, path)
        )
        worker.download_error.connect(
            lambda e, i=dl_id: self._on_error(i, e)
        )
        worker.download_cancelled.connect(
            lambda i=dl_id: self._on_cancelled(i)
        )
        worker.finished.connect(lambda i=dl_id: self._on_finished(i))

        self._workers[dl_id] = {
            "worker": worker,
            "url": url,
            "title": title,
            "options": options,
            "started": False,
            "done": False,
        }

        self.download_added.emit(dl_id, title)
        self._queue.append(dl_id)
        if self._running_count() >= self._max_concurrent:
            self.download_status.emit(dl_id, "Queued")
        self._start_queued()

        return dl_id

    def _running_count(self):
        return sum(1 for i in self._workers.values() if i["started"] and not i["done"])

    def _start_queued(self):
        while self._queue and self._running_count() < self._max_concurrent:
            dl_id = self._queue.pop(0)
            info = self._workers.get(dl_id)
            if not info:
                continue
            info["started"] = True
            info["worker"].start()
            self.download_started.emit(dl_id)

    def cancel_download(self, dl_id):
        info = self._workers.get(dl_id)
        if not info or info["done"]:
            return
        if not info["started"]:
            # Never started: drop it from the queue right away.
            if dl_id in self._queue:
                self._queue.remove(dl_id)
            info["done"] = True
            self._workers.pop(dl_id, None)
            info["worker"].deleteLater()
            self.download_cancelled.emit(dl_id)
            return
        info["worker"].cancel()
        self.download_status.emit(dl_id, "Cancelling")

    def cancel_all(self, wait_ms=5000):
        for dl_id in list(self._workers):
            self.cancel_download(dl_id)
        for info in list(self._workers.values()):
            info["worker"].wait(wait_ms)

    def _on_complete(self, dl_id, title, path):
        info = self._workers.get(dl_id)
        if info:
            info["done"] = True
            info["title"] = title
            self._save_history(info["url"], title, info.get("options", {}))
        self.download_complete.emit(dl_id, title, path)

    def _on_error(self, dl_id, message):
        info = self._workers.get(dl_id)
        if info:
            info["done"] = True
        self.download_error.emit(dl_id, message)

    def _on_cancelled(self, dl_id):
        info = self._workers.get(dl_id)
        if info:
            info["done"] = True
        self.download_cancelled.emit(dl_id)

    def _on_finished(self, dl_id):
        info = self._workers.pop(dl_id, None)
        if info:
            info["worker"].deleteLater()
        self._start_queued()

    def _save_history(self, url, title, options):
        try:
            with open(self._history_file, "a", encoding="utf-8") as f:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fmt = options.get("format", "N/A")
                f.write(f"[{ts}] {title}\n")
                f.write(f"  URL: {url}\n")
                f.write(f"  Format: {fmt}\n")
                f.write("-" * 80 + "\n")
        except Exception:
            pass

    def get_history(self):
        if os.path.exists(self._history_file):
            try:
                with open(self._history_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return ""
        return ""
