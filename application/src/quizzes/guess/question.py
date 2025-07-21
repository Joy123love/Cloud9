from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from theming.theme import theme
from theming.font import font


class GuessQuestion(QWidget):
    def __init__(self, question: str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();

        self.text = QLabel(question);
        self.text.setFont(font.heading);
        self.text.setStyleSheet(f"color: {theme.text.name()}")
        layout.addWidget(self.text);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

