from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from ..editor.limits import Limits
from .sidebar import CreateSidebar
from ..details import ChallengeDetails
from .controls import CreateMenu
from .editor import CreateCodeEditor


class CreateCodingGameScreen(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);

        editor_layout = QVBoxLayout();
        self.menu = CreateMenu();
        editor_layout.addWidget(self.menu);
        self.editor = CreateCodeEditor("10", "10");
        editor_layout.addWidget(self.editor);

        right = QWidget();
        right.setLayout(editor_layout);

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);

        self.side = CreateSidebar(ChallengeDetails("Test Project", "Taida", "Finish The App", "hello()", Limits().keywords, ["x == 19"],));

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.side);
        self.setCentralWidget(right)
