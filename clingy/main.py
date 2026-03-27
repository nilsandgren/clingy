"""Clingy – Colorful notes for your desktop"""

import sys

from PySide6.QtWidgets import QApplication

from clingy.note_manager import NoteManager
from clingy.tray_icon import TrayIcon, app_icon


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("Clingy")
    app.setDesktopFileName("clingy")
    app.setWindowIcon(app_icon())

    # Keep the app running when all windows are hidden (tray keeps it alive).
    app.setQuitOnLastWindowClosed(False)

    manager = NoteManager()
    tray = TrayIcon(manager)
    tray.show()

    # Restore previously saved notes.
    manager.load_all()

    # If there are no saved notes, create a default one.
    if manager.note_count() == 0:
        manager.create_note()

    # Bring all notes to the front so they are not hidden behind other windows.
    manager.show_all()

    # Save everything on shutdown.
    app.aboutToQuit.connect(manager.save_all)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
