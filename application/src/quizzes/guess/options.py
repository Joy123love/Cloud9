from PyQt6.QtGui import QIcon, QPalette
from PyQt6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QTextEdit, QVBoxLayout, QWidget

from assets.icons import icons
from theming.font import font
from theming.theme import theme
from widgets.text.line import LineTextEdit

class Option(QPushButton):
    def __init__(self, pos : int, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.position = pos;
        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background: {theme.background.name()}; color: {theme.text.name()}; border-radius: 10px; padding : 5px")
        self.setFont(font.default);

class GuessQuizOptions(QWidget):
    def __init__(self, options : list[str], *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QGridLayout();

        for i, option in enumerate(options):
            layout.addWidget(Option(i, option));

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

