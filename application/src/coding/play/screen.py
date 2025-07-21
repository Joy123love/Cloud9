from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ..editor.limits import Limits
from ..editor.widget import CodeEditor
from .sidebar import PlaySidebar
from ..details import ChallengeDetails
from .controls import PlayMenu


class PlayCodingGameScreen(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);

        editor_layout = QVBoxLayout();
        self.menu = PlayMenu();
        editor_layout.addWidget(self.menu);
        self.editor = CodeEditor("10");
        editor_layout.addWidget(self.editor);

        right = QWidget();
        right.setLayout(editor_layout);

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);

        self.side = PlaySidebar(ChallengeDetails("Test Project", "Taida", "Finish The App", "hello()", Limits().keywords, ["x == 19"],));

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.side);
        self.setCentralWidget(right)
