from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from theming.theme import theme
from theming.font import font


class CreateQuestion(QWidget):
    def __init__(self, question: str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();

        # self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        # self.setAutoFillBackground(True)
        # self.setStyleSheet(f"background: {theme.background.name()}; border-radius: 10px; padding : 5px")

        self.input = QTextEdit(question);
        self.input.setFont(font.sub_heading);
        self.input.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background_alternative.name()};")
        self.input.setFixedHeight(250)
        layout.addWidget(self.input);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

