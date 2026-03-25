# Clingy

Create colorful, frameless sticky notes that float on your desktop. Notes
persist across restarts and the application lives in the system tray.

## Features

- **Frameless windows** — no title bar or standard window decorations.
- **Multiple notes** — create as many notes as you need.
- **Drag to move** — click and drag the title area to reposition a note.
- **Resize** — drag the grip in the bottom-right corner.
- **Color themes** — click the color dot to pick from six pastel themes.
- **Rich text** — bold, italic, underline, bullet lists and font-size changes.
- **Persistence** — notes are saved as JSON files in `~/.local/share/clingy/`.
- **System tray** — click the tray icon to create notes, show/hide all, or quit.

## Keyboard Shortcuts

| Shortcut             | Action                |
|----------------------|-----------------------|
| `Ctrl+B`             | Bold                  |
| `Ctrl+I`             | Italic                |
| `Ctrl+U`             | Underline             |
| `Ctrl+Shift+L`       | Toggle bullet list    |
| `Ctrl++` / `Ctrl+=`  | Increase font size    |
| `Ctrl+-`             | Decrease font size    |
| `Ctrl+M`             | Minimize/restore      |

## Quick Start

```bash
# 1. Create a virtual environment and install dependencies
./setup.sh

# 2. Launch the application
./run.sh
```

### Manual Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m clingy.main
```

## Requirements

- Python 3.10+
- PySide6 >= 6.5.0

## Notes on Linux Desktop Environments

- **GNOME 40+**: The system tray icon requires the
  [AppIndicator / KStatusNotifierItem](https://extensions.gnome.org/extension/615/appindicator-support/)
  GNOME Shell extension to be visible.
- **KDE Plasma / XFCE / LXQt**: System tray works out of the box.
- **Wayland**: Window dragging uses `QWindow.startSystemMove()` when available,
  with an X11-compatible fallback.
- **Tiling WMs** (i3, sway, Hyprland): Notes use the `Qt.Tool` window flag so
  most tiling WMs will float them automatically.

## Data Storage

Notes are saved as individual JSON files in `~/.local/share/clingy/`
(or `$XDG_DATA_HOME/clingy/` if set).  Each file contains the note's
content (HTML), color theme, position, size and timestamps.

## Project Structure

```
widget/
├── setup.sh             # Create venv & install deps
├── run.sh               # Launch the app
├── requirements.txt     # Python dependencies
└── clingy/
    ├── main.py          # Application entry point
    ├── note_manager.py  # Note lifecycle & persistence orchestration
    ├── note_window.py   # Frameless sticky-note QWidget
    ├── note_editor.py   # Rich-text QTextEdit with formatting shortcuts
    ├── title_bar.py     # Custom title bar (drag, color picker, buttons)
    ├── resize_grip.py   # Corner resize handle
    ├── tray_icon.py     # System tray icon & menu
    ├── persistence.py   # JSON file load/save (atomic writes)
    └── theme.py         # Color theme definitions
```
