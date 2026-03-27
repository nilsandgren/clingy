"""Frameless sticky note window.

Composes TitleBar, NoteEditor and ResizeGrip into a single frameless,
translucent QWidget that looks and feels like a macOS Sticky.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QPoint, QSize, QTimer
from PySide6.QtGui import QColor, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from clingy.note_editor import NoteEditor
from clingy.resize_grip import ResizeGrip
from clingy.theme import DEFAULT_THEME, get_theme
from clingy.title_bar import TitleBar

if TYPE_CHECKING:
    from clingy.note_manager import NoteManager

# Default dimensions for a new note.
DEFAULT_WIDTH = 250
DEFAULT_HEIGHT = 250


class NoteWindow(QWidget):
    """A single frameless sticky-note window."""

    def __init__(
        self,
        note_id: str,
        manager: NoteManager,
        color: str = DEFAULT_THEME,
        content: str = "",
        position: QPoint | None = None,
        size: QSize | None = None,
        created_at: str | None = None,
        minimized: bool = False,
    ):
        super().__init__()
        self.note_id = note_id
        self._manager = manager
        self._color_name = color
        self._theme = get_theme(color)
        self._created_at = created_at or datetime.now().isoformat()

        # Minimize state.
        self._minimized = False  # will be set via toggle_minimize() below
        self._expanded_size: QSize | None = None

        # Window flags: frameless window (appears in taskbar / Alt-Tab).
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Geometry.
        sz = size or QSize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.resize(sz)
        if position is not None:
            self.move(position)

        # -- Build UI -------------------------------------------------------
        self._build_ui()

        # Set initial content *after* the editor is created.
        if content:
            self.editor.blockSignals(True)
            self.editor.setHtml(content)
            self.editor.blockSignals(False)

        # Debounced auto-save timer (1 s after last edit).
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(1000)
        self._save_timer.timeout.connect(self._auto_save)
        self.editor.textChanged.connect(self._save_timer.start)

        # Ctrl+M shortcut to minimize/restore.
        shortcut = QShortcut(QKeySequence("Ctrl+M"), self)
        shortcut.setContext(Qt.WindowShortcut)
        shortcut.activated.connect(self.toggle_minimize)

        # Apply initial minimized state if requested (must be after timer setup).
        if minimized:
            self.toggle_minimize()

    # -- Public API ----------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise the note's state to a dict suitable for JSON storage."""
        # When minimized, persist the expanded size so it restores correctly.
        if self._minimized and self._expanded_size is not None:
            w, h = self._expanded_size.width(), self._expanded_size.height()
        else:
            w, h = self.width(), self.height()
        return {
            "id": self.note_id,
            "color": self._color_name,
            "content_html": self.editor.toHtml(),
            "position": {"x": self.pos().x(), "y": self.pos().y()},
            "size": {"width": w, "height": h},
            "created_at": self._created_at,
            "minimized": self._minimized,
        }

    def set_color_theme(self, name: str) -> None:
        """Change the note's color theme and repaint."""
        self._color_name = name
        self._theme = get_theme(name)
        self._title_bar.set_theme_colors(
            self._theme["title_bar"],
            self._theme["accent"],
            self._theme["text_color"],
        )
        self.editor.set_text_color(self._theme["text_color"])
        self._resize_grip.set_accent_color(self._theme["accent"])
        self.update()
        self._schedule_save()

    def on_geometry_changed(self) -> None:
        """Called by TitleBar / ResizeGrip after a drag or resize finishes."""
        self._schedule_save()

    def toggle_minimize(self) -> None:
        """Toggle between minimized (title bar only) and expanded state."""
        pos = self.pos()
        if not self._minimized:
            # Collapse: remember expanded size, shrink to title bar height.
            self._expanded_size = self.size()
            title_h = self._title_bar.height()
            self.editor.hide()
            self._resize_grip.hide()
            self.setFixedHeight(title_h)
            self._minimized = True
            self._title_bar.set_minimized(True, self._first_line_text())
        else:
            # Expand: restore the remembered size.
            self._minimized = False
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
            sz = self._expanded_size or QSize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
            self.resize(sz)
            self.editor.show()
            self._resize_grip.show()
            self._title_bar.set_minimized(False)
        # Keep the top edge at the same position.
        self.move(pos)
        self.update()
        self._schedule_save()

    # -- Internal build ------------------------------------------------------

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Title bar.
        self._title_bar = TitleBar(
            title_color=self._theme["title_bar"],
            accent_color=self._theme["accent"],
            text_color=self._theme["text_color"],
        )
        self._title_bar.close_requested.connect(self._on_close)
        self._title_bar.new_note_requested.connect(self._on_new_note)
        self._title_bar.minimize_requested.connect(self.toggle_minimize)
        self._title_bar.color_changed.connect(self.set_color_theme)
        root_layout.addWidget(self._title_bar)

        # Editor.
        self.editor = NoteEditor(text_color=self._theme["text_color"])
        root_layout.addWidget(self.editor, stretch=1)

        # Bottom row: spacer + resize grip.
        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(0)
        bottom.addStretch(1)
        self._resize_grip = ResizeGrip(accent_color=self._theme["accent"])
        bottom.addWidget(self._resize_grip)
        root_layout.addLayout(bottom)

    # -- Painting (rounded background) --------------------------------------

    def paintEvent(self, _event) -> None:  # noqa: N802
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(self._theme["background"]))
        p.setPen(Qt.NoPen)
        if self._minimized:
            # When collapsed the title bar paints itself fully rounded,
            # so just fill behind it with the same radius.
            p.drawRoundedRect(self.rect(), 10, 10)
        else:
            p.drawRoundedRect(self.rect(), 10, 10)
        p.end()

    # -- Slots ---------------------------------------------------------------

    def _on_close(self) -> None:
        self._manager.delete_note(self.note_id)

    def _on_new_note(self) -> None:
        self._manager.create_note()

    def _schedule_save(self) -> None:
        """Reset the debounce timer so a save happens soon."""
        self._save_timer.start()

    def _auto_save(self) -> None:
        self._manager.save_note(self.note_id)

    def _first_line_text(self) -> str:
        """Extract the first non-empty line of plain text from the editor."""
        text = self.editor.toPlainText()
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                # Truncate long lines so they fit in the title bar.
                return stripped[:60] + ("\u2026" if len(stripped) > 60 else "")
        return ""
