from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit, QTextEdit

from theming.theme import theme
from theming.font import font


class LineTextEdit(QLineEdit):
    def __init__(self, text = "", placeholder = "", font : QFont = font.small, height : int = 30, color = theme.text,*args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setText(text);
        self.setFont(font);
        self.setPlaceholderText(placeholder);
        self.setFixedHeight(height)
        self.setStyleSheet(f"color: {color.name()}")
