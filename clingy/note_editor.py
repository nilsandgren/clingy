"""Rich-text editor widget for sticky notes.

Provides a QTextEdit subclass with keyboard shortcuts for common
formatting operations (bold, italic, underline, bullet lists, font size).
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QFont,
    QKeySequence,
    QShortcut,
    QTextBlockFormat,
    QTextCharFormat,
    QTextListFormat,
)
from PySide6.QtWidgets import QTextEdit


class NoteEditor(QTextEdit):
    """QTextEdit with rich-text formatting keyboard shortcuts."""

    def __init__(self, text_color: str = "#333333", parent=None):
        super().__init__(parent)
        self._setup_style(text_color)
        self._setup_shortcuts()

    # -- Public API ----------------------------------------------------------

    def set_text_color(self, color: str) -> None:
        """Update the editor's default text color to match the theme."""
        self._setup_style(color)

    # -- Internal setup ------------------------------------------------------

    def _setup_style(self, text_color: str) -> None:
        self.setStyleSheet(f"""
            QTextEdit {{
                background: transparent;
                border: none;
                padding: 6px 8px;
                color: {text_color};
                font-size: 14px;
                selection-background-color: rgba(0, 0, 0, 40);
            }}
        """)
        self.setAcceptRichText(True)

    def _setup_shortcuts(self) -> None:
        """Register formatting keyboard shortcuts."""
        shortcuts = {
            "Ctrl+B":       self._toggle_bold,
            "Ctrl+I":       self._toggle_italic,
            "Ctrl+U":       self._toggle_underline,
            "Ctrl+Shift+L": self._toggle_bullet_list,
            "Ctrl++":       self._increase_font_size,
            "Ctrl+=":       self._increase_font_size,   # without Shift
            "Ctrl+-":       self._decrease_font_size,
        }
        for key, slot in shortcuts.items():
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.setContext(Qt.WidgetShortcut)
            shortcut.activated.connect(slot)

    # -- Formatting helpers --------------------------------------------------

    def _toggle_bold(self) -> None:
        fmt = self.currentCharFormat()
        weight = QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold
        fmt.setFontWeight(weight)
        self.mergeCurrentCharFormat(fmt)

    def _toggle_italic(self) -> None:
        fmt = self.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.mergeCurrentCharFormat(fmt)

    def _toggle_underline(self) -> None:
        fmt = self.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.mergeCurrentCharFormat(fmt)

    def _toggle_bullet_list(self) -> None:
        cursor = self.textCursor()
        current_list = cursor.currentList()
        if current_list:
            # Remove list formatting by resetting the block format.
            block_fmt = QTextBlockFormat()
            cursor.setBlockFormat(block_fmt)
            # Also remove the block from its list.
            current_list.remove(cursor.block())
        else:
            list_fmt = QTextListFormat()
            list_fmt.setStyle(QTextListFormat.ListDisc)
            cursor.createList(list_fmt)
        self.setTextCursor(cursor)

    def _increase_font_size(self) -> None:
        self._adjust_font_size(1)

    def _decrease_font_size(self) -> None:
        self._adjust_font_size(-1)

    def _adjust_font_size(self, delta: int) -> None:
        fmt = self.currentCharFormat()
        size = fmt.fontPointSize()
        if size < 1:
            size = self.font().pointSize()
        new_size = max(6, min(72, size + delta))
        fmt = QTextCharFormat()
        fmt.setFontPointSize(new_size)
        self.mergeCurrentCharFormat(fmt)
