"""Note lifecycle manager.

Creates, deletes, tracks and persists sticky note windows.
"""

from __future__ import annotations

import uuid
from typing import Optional

from PySide6.QtCore import QObject, QPoint, QSize, QTimer, Signal
from PySide6.QtWidgets import QApplication

from clingy.note_window import NoteWindow
from clingy.persistence import delete_note_file, load_all_notes, save_note
from clingy.theme import DEFAULT_THEME


class NoteManager(QObject):
    """Manages the collection of open sticky notes."""

    note_created = Signal(str)
    note_deleted = Signal(str)

    # Auto-save interval in milliseconds (30 seconds).
    AUTO_SAVE_INTERVAL = 30_000

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._notes: dict[str, NoteWindow] = {}

        # Periodic auto-save timer.
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.setInterval(self.AUTO_SAVE_INTERVAL)
        self._auto_save_timer.timeout.connect(self.save_all)
        self._auto_save_timer.start()

    # -- Public API ----------------------------------------------------------

    def note_count(self) -> int:
        return len(self._notes)

    def create_note(
        self,
        color: str = DEFAULT_THEME,
        position: Optional[QPoint] = None,
        size: Optional[QSize] = None,
        content: str = "",
        note_id: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> NoteWindow:
        """Create a new sticky note and show it."""
        if note_id is None:
            note_id = uuid.uuid4().hex[:12]
        if position is None:
            position = self._next_note_position()

        win = NoteWindow(
            note_id=note_id,
            manager=self,
            color=color,
            content=content,
            position=position,
            size=size,
            created_at=created_at,
        )
        self._notes[note_id] = win
        win.show()
        self.note_created.emit(note_id)
        # Persist immediately so the note survives a crash right after creation.
        self.save_note(note_id)
        return win

    def delete_note(self, note_id: str) -> None:
        """Close and permanently remove a note."""
        win = self._notes.pop(note_id, None)
        if win is not None:
            win.close()
            win.deleteLater()
        delete_note_file(note_id)
        self.note_deleted.emit(note_id)

    def save_note(self, note_id: str) -> None:
        """Persist a single note to disk."""
        win = self._notes.get(note_id)
        if win is not None:
            save_note(note_id, win.to_dict())

    def save_all(self) -> None:
        """Persist every open note to disk."""
        for note_id in list(self._notes):
            self.save_note(note_id)

    def load_all(self) -> None:
        """Load all previously saved notes from disk."""
        for data in load_all_notes():
            self.create_note(
                note_id=data.get("id"),
                color=data.get("color", DEFAULT_THEME),
                content=data.get("content_html", ""),
                position=_point_from_dict(data.get("position")),
                size=_size_from_dict(data.get("size")),
                created_at=data.get("created_at"),
            )

    def show_all(self) -> None:
        """Show (raise) all note windows."""
        for win in self._notes.values():
            win.show()
            win.raise_()
            win.activateWindow()

    def hide_all(self) -> None:
        """Hide all note windows."""
        for win in self._notes.values():
            win.hide()

    def toggle_visibility(self) -> None:
        """Toggle visibility of all notes."""
        if any(win.isVisible() for win in self._notes.values()):
            self.hide_all()
        else:
            self.show_all()

    # -- Helpers -------------------------------------------------------------

    def _next_note_position(self) -> QPoint:
        """Calculate a reasonable position for a newly created note.

        Offsets from the last note to avoid exact stacking.  Falls back to
        a sensible default if there are no existing notes.
        """
        if self._notes:
            last = list(self._notes.values())[-1]
            pos = last.pos() + QPoint(30, 30)
        else:
            pos = QPoint(100, 100)

        # Clamp to screen bounds so notes are not created off-screen.
        screen = QApplication.primaryScreen()
        if screen is not None:
            geom = screen.availableGeometry()
            pos.setX(min(pos.x(), geom.right() - 260))
            pos.setY(min(pos.y(), geom.bottom() - 260))
            pos.setX(max(pos.x(), geom.left()))
            pos.setY(max(pos.y(), geom.top()))
        return pos


# -- Module-level helpers ----------------------------------------------------

def _point_from_dict(d: dict | None) -> QPoint | None:
    if d and "x" in d and "y" in d:
        return QPoint(int(d["x"]), int(d["y"]))
    return None


def _size_from_dict(d: dict | None) -> QSize | None:
    if d and "width" in d and "height" in d:
        return QSize(int(d["width"]), int(d["height"]))
    return None
