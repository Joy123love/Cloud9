from typing import Dict
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QDockWidget, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QPushButton

from coding.editor.widget import font, theme

class CreateMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QHBoxLayout();
        
        self.submit = QPushButton();
        self.submit.setText("Submit");
        self.submit.setFont(font.default);
        self.submit.setAutoFillBackground(True);
        self.submit.setStyleSheet(f"background-color : {theme.background_alternative.name()};color: {theme.primary.name()}; border-radius: 10px; padding : 5px")
        layout.addWidget(self.submit, 0, Qt.AlignmentFlag.AlignRight);
        
        self.run = QPushButton();
        self.run.setText("Run");
        self.run.setFont(font.default);
        self.run.setAutoFillBackground(True);
        self.run.setStyleSheet(f"background-color : {theme.background_alternative.name()};color: {theme.secondary.name()}; border-radius: 10px; padding : 5px");
        layout.addWidget(self.run, 0, Qt.AlignmentFlag.AlignRight);

        layout.setSpacing(0);
        layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout);
