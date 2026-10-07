import os
import subprocess
import sys

from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QProgressBar, QSizePolicy, QVBoxLayout,
)

import theme
from widgets.common import ElidedLabel, icon_button


def _format_size(n):
    size = float(n)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024:
            return f"{size:.2f}{unit}" if unit != "B" else f"{int(size)}B"
        size /= 1024
    return f"{size:.2f}TiB"


def _repolish(w):
    w.style().unpolish(w)
    w.style().polish(w)
    w.update()


class DownloadItemWidget(QFrame):
    """One row in the downloads list: title, status, thin progress bar,
    tabular metrics and icon actions (cancel / show in folder / remove)."""

    cancel_clicked = pyqtSignal(int)
    close_clicked = pyqtSignal(int)

    def __init__(self, download_id, title, out_dir="", parent=None):
        super().__init__(parent)
        self.setObjectName("DownloadItem")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.download_id = download_id
        self.out_dir = out_dir
        self.result_path = ""
        self._finished = False
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._setup_ui(title)

    def _setup_ui(self, title):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 12, 12)
        lay.setSpacing(0)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(4)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(2)
        self.title_label = ElidedLabel(title)
        self.title_label.setObjectName("ItemTitle")
        self.title_label.setToolTip(title)
        text_col.addWidget(self.title_label)
        self.status_label = ElidedLabel("Waiting")
        self.status_label.setObjectName("ItemStatus")
        text_col.addWidget(self.status_label)
        top.addLayout(text_col, 1)
        top.addSpacing(8)

        self.folder_btn = icon_button("folder", "Show in folder")
        self.folder_btn.clicked.connect(self._open_location)
        top.addWidget(self.folder_btn, 0, Qt.AlignmentFlag.AlignTop)

        self.cancel_btn = icon_button("close", "Cancel download", danger=True)
        self.cancel_btn.clicked.connect(self._on_button_clicked)
        top.addWidget(self.cancel_btn, 0, Qt.AlignmentFlag.AlignTop)
        lay.addLayout(top)
        lay.addSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        lay.addWidget(self.progress_bar)
        lay.addSpacing(8)

        metrics = QHBoxLayout()
        metrics.setContentsMargins(0, 0, 4, 0)
        metrics.setSpacing(16)
        self.percent_label = QLabel("0.0%")
        self.speed_label = QLabel("")
        self.eta_label = QLabel("")
        self.size_label = QLabel("")
        for w in (self.percent_label, self.speed_label, self.eta_label):
            w.setObjectName("Metric")
            metrics.addWidget(w)
        metrics.addStretch(1)
        self.size_label.setObjectName("Metric")
        metrics.addWidget(self.size_label)
        lay.addLayout(metrics)

    # -------------------------------------------------------------- actions

    def _on_button_clicked(self):
        if self._finished:
            self.close_clicked.emit(self.download_id)
        else:
            self.cancel_btn.setEnabled(False)
            self.cancel_clicked.emit(self.download_id)

    def _open_location(self):
        path = self.result_path
        if path and os.path.isfile(path) and sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            return
        folder = path if path and os.path.isdir(path) else self.out_dir
        if folder and os.path.isdir(folder):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def _set_state(self, state):
        self.progress_bar.setProperty("state", state)
        self.status_label.setProperty("state", state)
        _repolish(self.progress_bar)
        _repolish(self.status_label)

    def _finish(self):
        self._finished = True
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.setToolTip("Remove from list")
        self.cancel_btn.setProperty("danger", False)
        _repolish(self.cancel_btn)
        self.speed_label.setText("")
        self.eta_label.setText("")

    def is_finished(self):
        return self._finished

    # --------------------------------------------------------------- updates

    def update_progress(self, percent_str, speed, eta, size=""):
        if self._finished:
            return
        try:
            val = float(percent_str.replace("%", "").strip())
            self.progress_bar.setValue(max(0, min(100, int(round(val)))))
            self.percent_label.setText(f"{val:.1f}%")
        except (ValueError, AttributeError):
            pass
        self.speed_label.setText(speed if speed and speed != "N/A" else "")
        self.eta_label.setText(f"ETA {eta}" if eta and eta != "N/A" else "")
        if size and size != "N/A":
            self.size_label.setText(size)

    def set_status(self, text):
        if self._finished:
            return
        self.status_label.setText(text)
        self._set_state("queued" if text.lower().startswith("queued") else "")

    def set_complete(self, title, path=""):
        self.result_path = path or ""
        self.progress_bar.setValue(100)
        self.percent_label.setText("100%")
        self.title_label.setText(title)
        self.title_label.setToolTip(title)
        status = "Completed"
        if self.result_path and os.path.isfile(self.result_path):
            # Show what was produced (several rows can share a title) and
            # the real final size rather than the last stream's size.
            ext = os.path.splitext(self.result_path)[1].lstrip(".").upper()
            if ext:
                status += f"  ·  {ext}"
            self.size_label.setText(_format_size(os.path.getsize(self.result_path)))
        self.status_label.setText(status)
        self.status_label.setToolTip(self.result_path)
        self._set_state("done")
        self._finish()

    def set_error(self, message):
        self.progress_bar.setValue(100)
        self.percent_label.setText("")
        self.size_label.setText("")
        self.status_label.setText(f"Failed: {message}")
        self.status_label.setToolTip(message)
        self._set_state("error")
        self._finish()

    def set_cancelled(self):
        self.status_label.setText("Cancelled")
        self._set_state("cancelled")
        self._finish()
