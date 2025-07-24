
from functools import partial
from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
import requests

from constants import SERVER_URL
from dashboard.banner import BannerFrame
from coding.details import ChallengeDetails
from utils import get_project_root
from theming.theme import theme
from theming.font import font;
import routes


class FetchChallengesThread(QThread):
    fetched = pyqtSignal(list)
    failed = pyqtSignal()

    def run(self):
        try:
            response = requests.get(SERVER_URL + "coding/list", timeout=5)
            if response.status_code == 200:
                data = response.json().get("challenges", [])
                if data:
                    self.fetched.emit(data)
                    return
            self.failed.emit()
        except Exception:
            self.failed.emit()

class ChallengeCard(BannerFrame):
    def __init__(self, name : str, username: str, points : str, func, *args, **kwargs):
        super().__init__(f"{get_project_root()}/src/assets/images/Coding.png", 0.3, *args, **kwargs);
        self.setMinimumSize(140, 220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet('background-color: rgba(117,178,222,0.10); border-radius: 14px;')
        self.mousePressEvent = partial(func);
        layout = QVBoxLayout();

        vcard_label = QLabel(name, self)
        vcard_label.setStyleSheet(f'color: {theme.text.name()}; font-weight: bold;')
        vcard_label.setFont(font.default);
        layout.addWidget(vcard_label)
        name_label = QLabel(f"By {username}", self)
        name_label.setStyleSheet(f'color: {theme.text.name()}; font-weight: bold;')
        name_label.setFont(font.small);
        layout.addWidget(name_label)
        points_label = QLabel(points, self)
        points_label.setFont(font.large);
        points_label.setStyleSheet(f'color: {theme.primary.name()}; font-weight: bold;')
        layout.addWidget(points_label)

        # widget = QWidget(parent=self);
        self.setLayout(layout)


class ChallengesCards(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.cthread = FetchChallengesThread();
        self.cthread.fetched.connect(self.fetched)
        self.cthread.failed.connect(self.failed)
        self.cthread.start()

    def fetched(self, data):
        self.challenges = data;
        self.init_ui()

    def failed(self):
        return
    
    def init_ui(self):
        from PyQt6.QtWidgets import QGridLayout, QSizePolicy
        games_grid = QGridLayout()
        games_grid.setSpacing(28)
        games_grid.setContentsMargins(0, 0, 0, 0)
        num_columns = 3
        for i, game in enumerate(self.challenges):
            vcard = ChallengeCard(
                game["name"], 
                game["username"], 
                str(game["points"]), 
                lambda e: routes.open_coding_play(ChallengeDetails(id = int(game["id"]), name=game["name"], user_id=game["user_id"], description="", starting="", statements={}, checks=[]))
            )
            row = i // num_columns
            col = i % num_columns
            games_grid.addWidget(vcard, row, col)
        
        for col in range(num_columns):
            games_grid.setColumnStretch(col, 1)
        
        self.setLayout(games_grid)
