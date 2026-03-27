"""System tray icon for the Clingy application.

Provides a tray icon with a context menu for creating notes, toggling
visibility, and quitting.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

if TYPE_CHECKING:
    from clingy.note_manager import NoteManager

# Path to the application icon bundled in the package.
_ICON_PATH = Path(__file__).resolve().parent / "resources" / "icons" / "clingy.png"


def app_icon() -> QIcon:
    """Return the shared Clingy application icon."""
    return QIcon(str(_ICON_PATH))


class TrayIcon(QSystemTrayIcon):
    """System-tray icon with a right-click context menu."""

    def __init__(self, manager: NoteManager):
        super().__init__()
        self._manager = manager

        self.setIcon(app_icon())
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

    # The application icon is now loaded from clingy/resources/icons/clingy.png
    # via the module-level app_icon() helper.
