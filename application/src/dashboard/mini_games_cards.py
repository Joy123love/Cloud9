from functools import partial
from typing import Any
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QWidget

from dashboard.banner import BannerFrame
from utils import get_project_root

class PopularCard(BannerFrame):
    def __init__(self, name : str, func, image : str, *args, **kwargs):
        super().__init__(f"{get_project_root()}/src/assets/images/{image}", 0, *args, **kwargs);
        self.setMinimumSize(140, 160)
        self.setStyleSheet('background-color: rgba(117,178,222,0.15); border-radius: 18px;')
        self.mousePressEvent = partial(func);
        
        label = QLabel(name, self)
        label.setStyleSheet('color: #fff; font-size: 16px; font-weight: bold;')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)


class PopularCards(QWidget):
    def __init__(self, games : list[dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs);
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet('background: transparent; border: none; QScrollBar:horizontal {height:0px;}')
        scroll_area.setFixedHeight(180)
        scroll_content = QFrame()
        scroll_content.setStyleSheet('background: transparent;')
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)
        
        for game in games:
            card = PopularCard(game["name"], game["func"], game["image"])
            scroll_layout.addWidget(card)

        self.setLayout(scroll_layout)
class GameCard(BannerFrame):
    def __init__(self, name : str, func, image, *args, **kwargs):
        super().__init__(f"{get_project_root()}/src/assets/images/{image}", 0, *args, **kwargs);
        self.setMinimumSize(140, 220)
        # self.setMaximumSize(300, 300)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet('background-color: rgba(117,178,222,0.10); border-radius: 14px;')
        vcard_label = QLabel(name, self)
        vcard_label.setStyleSheet('color: #fff; font-size: 15px; font-weight: bold;')
        vcard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vcard_label.setGeometry(0, 100, 140, 40)

class GamesCards(QWidget):
    def __init__(self, games : list[dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs);
        from PyQt6.QtWidgets import QGridLayout, QSizePolicy
        games_grid = QGridLayout()
        games_grid.setSpacing(28)
        games_grid.setContentsMargins(0, 0, 0, 0)
        num_columns = 3
        for i, game in enumerate(games):
            vcard = GameCard(game["name"], game["func"], game["image"])
            row = i // num_columns
            col = i % num_columns
            games_grid.addWidget(vcard, row, col)
        
        for col in range(num_columns):
            games_grid.setColumnStretch(col, 1)
        
        self.setLayout(games_grid)
