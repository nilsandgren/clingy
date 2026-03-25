"""Custom title bar for frameless sticky note windows.

Provides drag-to-move, a color picker (clicking the color dot),
a new-note button (+), a close button (x), and double-click to
minimize/restore.
"""

from PySide6.QtCore import Qt, Signal, QPoint, QSize
from PySide6.QtGui import QColor, QFont, QPainter, QMouseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from clingy.theme import THEMES, THEME_NAMES


# ---------------------------------------------------------------------------
# Color-dot widget (click to open color picker)
# ---------------------------------------------------------------------------

class _ColorDot(QWidget):
    """A small clickable circle showing the note's current theme color."""

    clicked = Signal()

    def __init__(self, color: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.PointingHandCursor)
        self._color = color

    def set_color(self, color: str) -> None:
        self._color = color
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(self._color).darker(130))
        p.setPen(Qt.NoPen)
        p.drawEllipse(2, 2, 12, 12)
        p.end()

    def mousePressEvent(self, _event) -> None:  # noqa: N802
        self.clicked.emit()


# ---------------------------------------------------------------------------
# Color-picker popup (shown when the color dot is clicked)
# ---------------------------------------------------------------------------

class _ColorPickerPopup(QWidget):
    """A small floating widget showing colored circles for each theme."""

    color_selected = Signal(str)  # emits theme name

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent, Qt.Popup)
        self.setFixedSize(len(THEME_NAMES) * 24 + 8, 28)
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # Background rounded rect.
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(QColor("#CCCCCC"))
        p.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 6, 6)
        # Draw a circle for each theme.
        for i, name in enumerate(THEME_NAMES):
            color = QColor(THEMES[name]["background"])
            p.setBrush(color)
            p.setPen(QColor(THEMES[name]["accent"]))
            x = 8 + i * 24
            p.drawEllipse(x, 6, 16, 16)
        p.end()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        x = int(event.position().x())
        for i, name in enumerate(THEME_NAMES):
            cx = 8 + i * 24
            if cx <= x <= cx + 16:
                self.color_selected.emit(name)
                self.close()
                return
        self.close()


# ---------------------------------------------------------------------------
# Title bar
# ---------------------------------------------------------------------------

class TitleBar(QWidget):
    """Custom 24-pixel-tall title bar with drag support."""

    close_requested = Signal()
    new_note_requested = Signal()
    minimize_requested = Signal()
    color_changed = Signal(str)  # emits theme name

    BUTTON_STYLE = """
        QPushButton {{
            background: transparent;
            border: none;
            color: {text};
            font-size: 15px;
            font-weight: bold;
            padding: 0;
        }}
        QPushButton:hover {{
            background: rgba(0, 0, 0, 30);
            border-radius: 3px;
        }}
    """

    def __init__(self, title_color: str, accent_color: str,
                 text_color: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self._title_color = title_color

        # Drag state.
        self._drag_start: QPoint | None = None
        self._window_start: QPoint | None = None

        # Layout -------------------------------------------------------
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 4, 0)
        layout.setSpacing(2)

        # Color dot.
        self._color_dot = _ColorDot(accent_color)
        self._color_dot.clicked.connect(self._show_color_picker)
        layout.addWidget(self._color_dot)

        # Spacer.
        layout.addStretch(1)

        # "+" button (new note).
        btn_style = self.BUTTON_STYLE.format(text=text_color)
        self._btn_new = QPushButton("+")
        self._btn_new.setFixedSize(20, 20)
        self._btn_new.setStyleSheet(btn_style)
        self._btn_new.setCursor(Qt.PointingHandCursor)
        self._btn_new.clicked.connect(self.new_note_requested)
        layout.addWidget(self._btn_new)

        # Close button.
        self._btn_close = QPushButton("\u00d7")  # multiplication sign ×
        self._btn_close.setFixedSize(20, 20)
        self._btn_close.setStyleSheet(btn_style)
        self._btn_close.setCursor(Qt.PointingHandCursor)
        self._btn_close.clicked.connect(self.close_requested)
        layout.addWidget(self._btn_close)

        # Preview label (visible only when minimized).
        self._preview_label = QLabel()
        self._preview_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._preview_label.hide()
        self._update_preview_style(text_color)
        # Inserted between the color dot and the stretch; initially hidden.
        layout.insertWidget(1, self._preview_label, stretch=1)

        self._is_minimized = False

    # -- Public API -------------------------------------------------------

    def set_theme_colors(self, title_color: str, accent_color: str,
                         text_color: str) -> None:
        """Update colors after a theme change."""
        self._title_color = title_color
        self._color_dot.set_color(accent_color)
        btn_style = self.BUTTON_STYLE.format(text=text_color)
        self._btn_new.setStyleSheet(btn_style)
        self._btn_close.setStyleSheet(btn_style)
        self._update_preview_style(text_color)
        self.update()

    def set_minimized(self, minimized: bool, preview_text: str = "") -> None:
        """Update the title bar appearance for minimized / expanded state."""
        self._is_minimized = minimized
        if minimized:
            self._preview_label.setText(preview_text)
            self._preview_label.show()
        else:
            self._preview_label.hide()
        self.update()

    # -- Painting ---------------------------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(self._title_color))
        p.setPen(Qt.NoPen)
        rect = self.rect()
        if self._is_minimized:
            # Fully rounded when the note is collapsed (no body below).
            p.drawRoundedRect(rect, 10, 10)
        else:
            # Rounded top corners, square bottom corners.
            # Draw full rounded rect then cover bottom corners.
            p.drawRoundedRect(rect.adjusted(0, 0, 0, 6), 10, 10)
            p.drawRect(rect.adjusted(0, rect.height() - 6, 0, 0))
        p.end()

    # -- Drag-to-move -----------------------------------------------------

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            # Try the Wayland-friendly system move first.
            win_handle = self.window().windowHandle()
            if win_handle:
                try:
                    win_handle.startSystemMove()
                    event.accept()
                    return
                except AttributeError:
                    pass
            # Fallback: manual drag tracking (X11 / older Qt).
            self._drag_start = event.globalPosition().toPoint()
            self._window_start = self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_start is not None and self._window_start is not None:
            delta = event.globalPosition().toPoint() - self._drag_start
            self.window().move(self._window_start + delta)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton and self._drag_start is not None:
            self._drag_start = None
            self._window_start = None
            win = self.window()
            if hasattr(win, "on_geometry_changed"):
                win.on_geometry_changed()
            event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.minimize_requested.emit()
            event.accept()

    # -- Color picker ----------------------------------------------------

    def _show_color_picker(self) -> None:
        popup = _ColorPickerPopup(self)
        popup.color_selected.connect(self.color_changed)
        # Position the popup just below the color dot.
        dot_pos = self._color_dot.mapToGlobal(QPoint(0, self._color_dot.height() + 4))
        popup.move(dot_pos)
        popup.show()

    def _update_preview_style(self, text_color: str) -> None:
        """Apply styling to the preview label."""
        self._preview_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                background: transparent;
                font-size: 11px;
                padding-left: 4px;
            }}
        """)
        font = self._preview_label.font()
        font.setItalic(True)
        self._preview_label.setFont(font)
