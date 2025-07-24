from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QWidget
from huggingface_hub.inference._generated.types.base import dataclass_with_extra
import requests

import routes
from constants import SERVER_URL

from ..editor.limits import Limits
from ..editor.widget import CodeEditor
from .sidebar import PlaySidebar
from ..details import ChallengeDetails
from .controls import PlayMenu

class FetchChallengeThread(QThread):
    fetched = pyqtSignal(ChallengeDetails)
    failed = pyqtSignal()
    
    def __init__(self, id, *args, **kwargs):
        self.id = id
        super().__init__(*args, **kwargs);

    def run(self):
        try:
            response = requests.get(SERVER_URL + "coding", json={"id" : self.id}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                statements_json = data["statements"];
                statements = {}
                for statement in statements_json:
                    statements[statement["keyword"]] = statement["amount"]
                checks_json = data["statements"];
                checks = []
                for check in checks_json:
                    checks.append(check)

                details = ChallengeDetails(data["name"], data["user_id"], data["description"], data["starting"], statements, checks)

                if data:
                    self.fetched.emit(details)
                    return
            self.failed.emit()
        except Exception:
            self.failed.emit()

class PlayCodingGameScreen(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        
        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);

        editor_layout = QVBoxLayout();
        self.menu = PlayMenu(self.run_editor);
        editor_layout.addWidget(self.menu);
        self.editor = CodeEditor("Loading...");
        editor_layout.addWidget(self.editor);
        self.setLayout(editor_layout)
    
    def load(self, details : ChallengeDetails):
        self.details = details;
        if details.description == "":
            self.cthread = FetchChallengeThread(self.details.id);
            self.cthread.fetched.connect(self.run);
            self.cthread.start();

        self.editor.setText(details.starting);

    def run_editor(self):
        if not self.details:
            return

        locals = self.editor.run(limits=Limits(self.details.statements));
        incorrect = []
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

        import routes;
        id, _ = routes.get_user()
        json = {"id" : self.details.id, "user_id" : int(id)};

        response = requests.post(
            SERVER_URL + "coding",
            json=json,
            timeout=5
        )

        if response.status_code == 200:
            QMessageBox.information(self, "Success", "Finished Challenge")
            if routes.open_dashboard:
                routes.open_dashboard()

        else:
            msg = response.json().get('message', 'Creation failed.')
            QMessageBox.warning(self, "Failed", msg)



    def run(self, details : ChallengeDetails):
        details.username = self.details.username
        routes.open_coding_play(details)



