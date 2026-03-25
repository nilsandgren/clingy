"""Custom resize grip widget for frameless sticky note windows.

Provides a small triangular grip in the bottom-right corner that the
user can click and drag to resize the parent window.
"""

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget

# Minimum allowed note dimensions.
MIN_WIDTH = 150
MIN_HEIGHT = 120


class ResizeGrip(QWidget):
    """A 16x16 resize grip drawn in the bottom-right corner of a note."""

    def __init__(self, accent_color: str = "#E0D86E", parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.SizeFDiagCursor)
        self._accent_color = accent_color
        self._drag_start: QPoint | None = None
        self._window_size_start = None

    # -- Public API ----------------------------------------------------------

    def set_accent_color(self, color: str) -> None:
        self._accent_color = color
        self.update()

    # -- Painting ------------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        """Draw three small diagonal lines as a resize indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(self._accent_color).darker(140))
        pen.setWidth(1)
        painter.setPen(pen)

        # Three diagonal lines from bottom-left toward top-right.
        offsets = [4, 8, 12]
        for off in offsets:
            painter.drawLine(off, self.height(), self.width(), off)
        painter.end()

    # -- Mouse handling (resize) ---------------------------------------------

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPosition().toPoint()
            self._window_size_start = self.window().size()
            event.accept()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_start is not None:
            delta = event.globalPosition().toPoint() - self._drag_start
            new_w = max(MIN_WIDTH, self._window_size_start.width() + delta.x())
            new_h = max(MIN_HEIGHT, self._window_size_start.height() + delta.y())
            self.window().resize(new_w, new_h)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._drag_start = None
            self._window_size_start = None
            # Notify the parent window so it can persist the new size.
            win = self.window()
            if hasattr(win, "on_geometry_changed"):
                win.on_geometry_changed()
            event.accept()
