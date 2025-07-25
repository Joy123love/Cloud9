from functools import partial
import json
import os
from typing import Callable
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QLinearGradient, QPainter, QPen, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget
import requests

from assets import icons
from dashboard.leaderboard import Leaderboard
from authentication.picture import FetchProfilePictureThread
from constants import SERVER_URL
from theming.theme import theme


class SidebarFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(120)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = 20
        # Gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, theme.primary)
        gradient.setColorAt(1, theme.danger)
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(QPen(theme.text, 1))
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), radius, radius)

class DashboardIcon(QSvgWidget):
    def __init__(self, index, icon_clicked, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setFixedSize(32, 32)
        self.setStyleSheet('background: transparent; color : white')
        self.mousePressEvent = lambda e: icon_clicked(index)


class DashboardSidebar(SidebarFrame):
    def __init__(self, sidebar_icon_clicked,*args, **kwargs):
        super().__init__(*args, **kwargs);
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addStretch()
        sidebar_layout.setSpacing(28)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_clicked_extenal = sidebar_icon_clicked;

        icon_paths : list[str] = ["home.svg", "docs-inverted.svg", "settings-inverted.svg"]
        self.icons = [];

        for idx, path in enumerate(icon_paths):
            icon = DashboardIcon(idx, self.icon_clicked, icons.get_path(path));
            self.icons.append(icon)
            sidebar_layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)

        sidebar_layout.addStretch()
        self.setLayout(sidebar_layout)

    def create_icon(self, path : str) -> QSvgWidget:
        icon = QSvgWidget(path);
        icon.setFixedSize(32, 32)
        icon.setStyleSheet('background: transparent; color : white')
        return icon

    def icon_clicked(self, idx : int):
        icon_paths = [
("home.svg", "home-inverted.svg"),
            ("docs.svg", "docs-inverted.svg"),
            ("settings.svg", "settings-inverted.svg"),
        ]
        for i, icon_widget in enumerate(self.icons):
            selected_path, unselected_path = icon_paths[i]
            icon_widget.load(icons.get_path(selected_path if idx == i else unselected_path))
        self.icon_clicked_extenal(idx);

class DashboardRightPanel(QFrame):
    def __init__(self, username, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setMinimumWidth(400);
        self.user_id=user_id;
        self.username = username
        self.init_ui()
        self.fetch_picture()

    def fetch_picture(self):
        self.profile_pic_thread = FetchProfilePictureThread(id=self.user_id);
        self.profile_pic_thread.fetched.connect(self.profile_picture_fetched);
        self.profile_pic_thread.start();


    def init_ui(self):
        self.setStyleSheet(f'background-color: {theme.background_alternative.name()}; border-radius: 20px;')
        right_panel_layout = QVBoxLayout(self)
        # User profile section
        profile_container = QVBoxLayout()
        profile_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        profile_container.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        # Top row: notification icon, name, profile pic
        self.top_row = QHBoxLayout()
        self.top_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # Notification icon
        # Load and tint notification icon SVG to white
        notif_icon = QSvgWidget(icons.get_path("notifications-tinted.svg"));
        notif_icon.setFixedSize(28, 28)
        notif_icon.setStyleSheet('background: transparent; margin-right: 8px;')
        # User name
        user_name = QLabel(self.username)
        user_name.setStyleSheet(f'color: {theme.text.name()}; font-size: 15px; font-weight: bold; padding: 0 12px;')
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Profile picture (circle placeholder)
        self.profile_pic = QLabel()
        self.profile_pic.setFixedSize(60, 60)
        self.profile_pic.setStyleSheet(f'background-color: {theme.danger.name()}; border-radius: 30px; border: 2px solid {theme.text.name()};')
        self.profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.profile_pic.mousePressEvent = lambda e: self.upload_profile_picture();
        self.profile_image = QPixmap(icons.get_path("account.svg"))
        self.profile_pic.setPixmap(self.profile_image)

        # Add to top row in new order
        self.top_row.addWidget(notif_icon)
        self.top_row.addStretch(1)
        self.top_row.addWidget(user_name)
        self.top_row.addStretch(1)
        self.top_row.addWidget(self.profile_pic)
        profile_container.addLayout(self.top_row)
        # Rank label below
        user_rank = QLabel('Rank: Grandmaster')
        user_rank.setStyleSheet(f'color: {theme.primary.name()}; font-size: 13px; margin-top: 8px;')
        user_rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_container.addWidget(user_rank)
        
        right_panel_layout.addLayout(profile_container)
        right_panel_layout.addSpacing(10);

        self.leaderboard = Leaderboard();
        self.leaderboard.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        leaderboard_layout = QVBoxLayout();
        leaderboard_layout.addWidget(self.leaderboard);
        leaderboard_layout.setAlignment(Qt.AlignmentFlag.AlignBottom);
        right_panel_layout.addLayout(leaderboard_layout, Qt.AlignmentFlag.AlignBottom)

        right_panel_layout.addStretch()

    def profile_picture_fetched(self, filepath : str):
        self.profile_image = QPixmap(filepath)
        self.profile_pic.setPixmap(self.profile_image);
        self.profile_pic.update()
    
    def upload_profile_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add a Profile Picture", "", "Images (*.svg *.jpeg *.png *.jpg)")
        self.profile_picture_fetched(file_path);
        with open(file_path, 'rb') as file:
            response = requests.post(SERVER_URL + "profile/picture", files={'file': file, "json" : json.dumps({"user_id" : self.user_id})})
