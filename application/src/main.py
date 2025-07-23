from enum import Enum
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QDockWidget, QMainWindow, QStackedWidget, QTabWidget, QWidget
from coding.details import ChallengeDetails

from theming.theme import get_palette_from_theme, theme
import routes
from constants import *
import sys

class Screens(QStackedWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.current_username = "Guest"
        self.setup_routes();
        self.setup_screens();
        self.dock = None;

    def setup_routes(self):
        routes.open_switch_runner = self.open_switch_runner
        routes.open_signup = self.open_signup_screen
        routes.open_login = self.open_login_screen
        routes.open_dashboard = self.open_dashboard_screen
        routes.open_coding_create = self.open_coding_create_screen
        routes.open_coding_play = self.open_coding_play_screen
    
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
        from coding.create.screen import CreateCodingGameScreen
        self.coding_create = CreateCodingGameScreen()
        self.addWidget(self.coding_create)
        from coding.play.screen import PlayCodingGameScreen
        self.coding_play = PlayCodingGameScreen()
        self.addWidget(self.coding_play)
        from switch_runner.screen import SwitchRunnerScreen
        self.switch_runner = SwitchRunnerScreen()
        self.addWidget(self.switch_runner)

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
        self.open_screen(SWITCH_RUNNER);
        self.switch_runner.play();
    
    def open_dashboard_screen(self, username="Guest"):
        self.current_username = username
        if routes.set_colour_role:
            routes.set_colour_role(QPalette.ColorRole.LinkVisited);
        from dashboard.screen import DashboardScreen
        self.removeWidget(self.dashboard)
        self.dashboard = DashboardScreen()
        self.insertWidget(MENU, self.dashboard)
        self.open_screen(MENU)
        self.open_screen(MENU)

    def open_coding_play_screen(self, details : ChallengeDetails):
        from coding.play.sidebar import PlaySidebar
        from coding.play.screen import PlayCodingGameScreen
        self.setPalette(get_palette_from_theme(theme));
        self.open_screen(PLAY_CODING)
        screen = self.currentWidget();
        if screen is PlayCodingGameScreen:
            screen.load(details);
        self.dock = PlaySidebar(details);
        window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock);

    def open_coding_create_screen(self, details : ChallengeDetails):
        from coding.create.sidebar import CreateSidebar
        # self.setPalette(get_palette_from_theme(theme));
        self.open_screen(CREATE_CODING)
        self.dock = CreateSidebar(details);
        window.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock);
    
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
