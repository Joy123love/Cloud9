from enum import Enum
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QDockWidget, QMainWindow, QStackedWidget, QTabWidget, QWidget
from coding.details import ChallengeDetails

from utils import get_project_root
from theming.theme import get_palette_from_theme, theme
import routes
from constants import *
import sys
import subprocess
import os


class Screens(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setup_routes();
        self.setup_screens();
        self.dock = None;
        self.username = "Guest";
        self.user_id=None;

    def setup_routes(self):
        routes.open_switch_runner = self.open_switch_runner
        routes.open_signup = self.open_signup_screen
        routes.open_login = self.open_login_screen
        routes.open_dashboard = self.open_dashboard_screen
        routes.open_coding_create = self.open_coding_create_screen
        routes.open_coding_play = self.open_coding_play_screen
        routes.set_user = self.set_user
        routes.get_user = self.get_user
        routes.open_flappy_learn = self.open_flappy_learn
    
    def setup_screens(self):
        from authentication.login import LoginScreen
        self.login = LoginScreen()
        self.addWidget(self.login)
        from authentication.signup import SignUpScreen
        self.signup = SignUpScreen()
        self.addWidget(self.signup)
        from dashboard.screen import DashboardScreen
        self.dashboard = DashboardScreen()
        self.addWidget(self.dashboard)

        from coding.play.screen import PlayCodingGameScreen
        self.coding_play = PlayCodingGameScreen()
        self.addWidget(self.coding_play)
        from coding.create.screen import CreateCodingGameScreen
        self.coding_create = CreateCodingGameScreen()
        self.addWidget(self.coding_create)
        from switch_runner.screen import SwitchRunnerScreen
        self.switch_runner = SwitchRunnerScreen()
        self.addWidget(self.switch_runner)
        from flappy_learn.screen import FlappyLearnScreen
        self.flappy_learn = FlappyLearnScreen()
        self.addWidget(self.flappy_learn)

    def open_screen(self, index : int):
        if self.dock is None:
            pass
        else:
            window.removeDockWidget(self.dock)
        self.setCurrentIndex(index)
    
    def open_login_screen(self):
        self.open_screen(LOGIN)

    def open_signup_screen(self):
        self.open_screen(SIGNUP) 
    
    def open_switch_runner(self):
        # Launch the new Switch Runner game as a separate process

        script_path = os.path.abspath(
            os.path.join(
                get_project_root(),
                "src/switch_runner/game.py"
            )
        )
        print(f"Launching Switch Runner at: {script_path}")
        subprocess.Popen([sys.executable, script_path])
    
    def open_dashboard_screen(self):
        from dashboard.screen import DashboardScreen

        self.dashboard.close();
        self.removeWidget(self.dashboard);
        self.dashboard = DashboardScreen(self.username, str(self.user_id))
        self.insertWidget(MENU, self.dashboard)
        self.open_screen(MENU)


    def set_user(self, user_id : str, name : str):
        self.user_id = user_id;
        os.environ["uid9"] = user_id;
        self.username = name;
    
    def get_user(self) -> tuple[str, str]:
        return (str(self.user_id), self.username)

    def open_coding_play_screen(self, details : ChallengeDetails):
        from coding.play.sidebar import PlaySidebar
        from coding.play.screen import PlayCodingGameScreen

        self.setPalette(get_palette_from_theme(theme));
        self.open_screen(PLAY_CODING)
        screen = self.currentWidget();
        screen.load(details);
        self.dock = PlaySidebar(details);
        window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock);

    def open_coding_create_screen(self, details : ChallengeDetails):
        from coding.create.sidebar import CreateSidebar
        self.open_screen(CREATE_CODING)
        screen = self.currentWidget();
        if self.user_id:
            details.user_id = int(self.user_id)
        else:
            from authentication.login import show_messagebox
            show_messagebox(self, QtWidgets.QMessageBox.Icon.Warning, "Error", "Coding mini-game requires login");

        self.dock = CreateSidebar(details);
        screen.load(details, self.dock);

        window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock);
    
    def open_flappy_learn(self):
        # Launch the new Flappy Learn game as a separate process
        script_path = os.path.abspath(
            os.path.join(
                get_project_root(),
                "src/flappy_learn/game.py"
            )
        )
        print(f"Launching Flappy Learn at: {script_path}")
        subprocess.Popen([sys.executable, script_path])

class ExtraMainScreen(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setMinimumSize(1280, 720);
        self.screens = Screens(parent=self);
        self.setCentralWidget(self.screens);
        routes.set_background_style = self.setStyleSheet
        routes.reset_palette = lambda : self.setPalette(get_palette_from_theme(theme));
        routes.set_colour_role = lambda x: self.setBackgroundRole(x);

        self.setPalette(get_palette_from_theme(theme));


app = QApplication(sys.argv)
window = ExtraMainScreen();
window.show()
sys.exit(app.exec())
