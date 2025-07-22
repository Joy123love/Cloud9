from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ..editor.limits import Limits
from ..editor.widget import CodeEditor
from .sidebar import PlaySidebar
from ..details import ChallengeDetails
from .controls import PlayMenu


class PlayCodingGameScreen(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        
        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);

        editor_layout = QVBoxLayout();
        self.menu = PlayMenu();
        editor_layout.addWidget(self.menu);
        self.editor = CodeEditor("Loading...");
        editor_layout.addWidget(self.editor);
        self.setLayout(editor_layout);

    def load(self, details : ChallengeDetails):
        self.editor.setText(details.starting);
