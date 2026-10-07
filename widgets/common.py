"""Small shared building blocks for the UI."""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPainter
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy,
)

import theme


class ElidedLabel(QLabel):
    """Single-line label that elides its text instead of growing/clipping."""

    def __init__(self, text="", parent=None, mode=Qt.TextElideMode.ElideRight):
        super().__init__(parent)
        self._full = ""
        self._mode = mode
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setText(text)

    def setText(self, text):
        self._full = text or ""
        self.setToolTip(self._full if len(self._full) > 40 else "")
        super().setText(self._full)
        self.update()

    def fullText(self):
        return self._full

    def minimumSizeHint(self):
        return QSize(0, super().minimumSizeHint().height())

    def sizeHint(self):
        w = self.fontMetrics().horizontalAdvance(self._full) + 2
        return QSize(min(w, self.maximumWidth()), super().sizeHint().height())

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(self.palette().color(self.foregroundRole()))
        p.setFont(self.font())
        rect = self.contentsRect()
        text = self.fontMetrics().elidedText(self._full, self._mode, rect.width())
        p.drawText(rect, int(self.alignment() | Qt.AlignmentFlag.AlignVCenter), text)
        p.end()


def section_label(text, parent=None):
    """Uppercase, letter-spaced section header (colour/size come from QSS)."""
    lbl = QLabel(text.upper(), parent)
    lbl.setObjectName("SectionLabel")
    f = QFont(lbl.font())
    f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)
    lbl.setFont(f)
    return lbl


def hairline(vertical=False, parent=None):
    line = QFrame(parent)
    line.setObjectName("Hairline")
    if vertical:
        line.setFixedWidth(1)
    else:
        line.setFixedHeight(1)
    return line


def icon_button(name, tooltip, color_key="text2", size=28, icon_px=16, danger=False):
    btn = QPushButton()
    btn.setObjectName("IconButton")
    btn.setFixedSize(size, size)
    btn.setToolTip(tooltip)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    if danger:
        btn.setProperty("danger", True)
    theme.bind_icon(btn, name, color_key, icon_px)
    return btn


class Segmented(QFrame):
    """A row of mutually exclusive toggle buttons; only the outer corners
    of the first/last segment are (slightly) rounded."""

    def __init__(self, labels, parent=None, compact=False, button_width=None):
        super().__init__(parent)
        self.setObjectName("Segmented")
        if compact:
            self.setProperty("compact", True)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons = []
        for i, label in enumerate(labels):
            b = QPushButton(label)
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            if button_width:
                b.setFixedWidth(button_width)
            if i == 0:
                b.setProperty("first", True)
            if i == len(labels) - 1:
                b.setProperty("last", True)
            self.group.addButton(b, i)
            self.buttons.append(b)
            lay.addWidget(b)
        if self.buttons:
            self.buttons[0].setChecked(True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def index(self):
        return self.group.checkedId()

    def set_index(self, i):
        if 0 <= i < len(self.buttons):
            self.buttons[i].setChecked(True)
