"""System tray icon for the Clingy application.

Provides a tray icon with a context menu for creating notes, toggling
visibility, and quitting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

if TYPE_CHECKING:
    from clingy.note_manager import NoteManager


class TrayIcon(QSystemTrayIcon):
    """System-tray icon with a right-click context menu."""

    def __init__(self, manager: NoteManager):
        super().__init__()
        self._manager = manager

        self.setIcon(self._create_icon())
        self.setToolTip("Clingy")

        # Context menu.
        menu = QMenu()

        new_action = QAction("New Note", menu)
        new_action.triggered.connect(self._manager.create_note)
        menu.addAction(new_action)

        menu.addSeparator()

        show_action = QAction("Show All Notes", menu)
        show_action.triggered.connect(self._manager.show_all)
        menu.addAction(show_action)

        hide_action = QAction("Hide All Notes", menu)
        hide_action.triggered.connect(self._manager.hide_all)
        menu.addAction(hide_action)

        menu.addSeparator()

        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._on_quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

        # Left-click toggles visibility of all notes.
        self.activated.connect(self._on_activated)

    # -- Slots ---------------------------------------------------------------

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.Trigger:  # single left click
            self._manager.toggle_visibility()

    def _on_quit(self) -> None:
        self._manager.save_all()
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    # -- Icon generation -----------------------------------------------------

    @staticmethod
    def _create_icon() -> QIcon:
        """Draw a simple sticky-note icon programmatically."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        # Note body.
        p.setBrush(QColor("#FDFD96"))
        p.setPen(QColor("#E0D86E"))
        p.drawRoundedRect(4, 4, 56, 56, 8, 8)
        # A couple of ruled lines.
        p.setPen(QColor("#D0D060"))
        for y in (22, 34, 46):
            p.drawLine(12, y, 52, y)
        p.end()
        return QIcon(pixmap)
