# Clingy

Create colorful sticky notes that float on your desktop. Notes
persist across restarts and the application lives in the system tray.

![Screenshot](./clingy.png)

## Features

- **System tray** — Click the tray icon to create notes, show/hide all, or quit.
- **Color themes** — Click the color dot to pick a color theme.
- **Rich text** — Bold, italic, underline, bullet lists and font-size changes.
- **Persistence** — Notes are saved as JSON files in `~/.local/share/clingy/`.

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

First the virtual Python environment containing Clingy's runtime dependencies needs to be created.
You only need to run this command once.

```bash
./setup.sh
```

Launch the application

```bash
./run.sh
```

## Requirements

- Python 3.10+
- PySide6 >= 6.5.0 (installed by setup.sh) 

Tested on Ubuntu 24.04 using GNOME with Wayland.
