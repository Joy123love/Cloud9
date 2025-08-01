from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget
import requests

from authentication import session
from ..editor.limits import Limits
from .sidebar import CreateSidebar
from ..details import ChallengeDetails
from .controls import CreateMenu
from .editor import CreateCodeEditor
import routes

class CreateCodingGameScreen(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        
        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);
        self.details = None;
        
        editor_layout = QVBoxLayout();
        self.menu = CreateMenu(self.run, self.submit);
        editor_layout.addWidget(self.menu);
        self.editor = CreateCodeEditor("Loading...", "Loading...");
        editor_layout.addWidget(self.editor);
        self.setLayout(editor_layout);

    def load(self, details : ChallengeDetails, sidebar : CreateSidebar):
        self.sidebar = sidebar;
        self.details = details;
        self.editor.start_editor.setText(self.details.starting);
        self.editor.solution_editor.setText(self.details.starting);
    
    def submit(self):
        from constants import SERVER_URL

        statements = [];
        for k, v in self.sidebar.bottom.statements.get_statements().items():
            statements.append({"keyword" : k, "amount" : v});
        user_id, _ = routes.get_user()
        json = {"name": self.sidebar.top.name.text(), "user_id" : user_id, "description": self.sidebar.top.description.toPlainText(), "starting" : self.editor.start_editor.text(), "checks" : self.sidebar.bottom.checks.get_checks(), "statements" : statements}

        response = requests.post(
            SERVER_URL + "coding",
            json=json,
            timeout=5
        )

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Created successfully")
            if routes.open_dashboard:
                routes.open_dashboard()

        else:
            msg = response.json().get('message', 'Creation failed.')
            QMessageBox.warning(self, "Failed", msg)

    def run(self):
        if not self.details:
            return

        if self.editor.tab.currentIndex() == 0:
            self.editor.start_editor.run()
        else:
            locals = self.editor.solution_editor.run(limits=Limits(self.sidebar.bottom.statements.get_statements()));
            incorrect = [];
            for check in self.details.checks:
                try:
                    correct = eval(check, locals);
                    if type(correct) is bool:
                        if correct:
                            continue;
                except:
                    incorrect.append(check)
                incorrect.append(check)
            
            if len(incorrect) > 0:
                from authentication.login import show_messagebox
                show_messagebox(self, QtWidgets.QMessageBox.Icon.Warning, "Error", f"Failed evaluation checks : {incorrect}")
                return;

