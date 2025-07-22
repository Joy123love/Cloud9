from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget
import requests

from ..editor.limits import Limits
from .sidebar import CreateSidebar
from ..details import ChallengeDetails
from .controls import CreateMenu
from .editor import CreateCodeEditor


class CreateCodingGameScreen(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        
        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);
        self.details = None;
        
        editor_layout = QVBoxLayout();
        self.menu = CreateMenu();
        editor_layout.addWidget(self.menu);
        self.editor = CreateCodeEditor("Loading...", "Loading...");
        editor_layout.addWidget(self.editor);
        self.setLayout(editor_layout);

    def load(self, details : ChallengeDetails):
        self.details = details;
        self.editor.start_editor.setText(self.details.starting);
        self.editor.solution_editor.setText(self.details.starting);
        # self.menu.run.clicked.connect(self.run)
        # self.menu.submit.clicked.connect(self.submit)
    
    def submit(self):
        from constants import SERVER_URL
        from main import window;
        from sidebar import CreateSidebar

        sidebar = window.screens.dock;
        if sidebar is not CreateSidebar:
            return;


        response = requests.post(
            SERVER_URL + "login",
            json={"name": sidebar.top.name.toPlainText(), "description": sidebar.top.description.toPlainText(), },
            timeout=5
        )
        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Logged in successfully!")
            from main import window
            # screens.open_dashboard_screen();
            # self.dashboard = DashboardWindow()
            # self.dashboard.show()
            # self.close()

        else:
            msg = response.json().get('message', 'Login failed.')
            QMessageBox.warning(self, "Failed", msg)

        if self.editor.tab.currentIndex() == 0:
            self.editor.start_editor.run()
        else:
            self.editor.solution_editor.run();

    def run(self):
        if not self.details:
            return

        if self.editor.tab.currentIndex() == 0:
            self.editor.start_editor.run()
        else:
            self.editor.solution_editor.run();

