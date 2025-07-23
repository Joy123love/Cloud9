import json
import os
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QLineEdit, QTableWidget, QTableWidgetItem,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
from constants import SERVER_URL
from theming.theme import theme

LEADERBOARD_URL = f"{SERVER_URL}leaderboard"  # Change to your server URL
LOCAL_FILE = "leaderboard.json"

class FetchLeaderboardThread(QThread):
    fetched = pyqtSignal(list)
    failed = pyqtSignal()

    def run(self):
        try:
            response = requests.get(LEADERBOARD_URL, timeout=5)
            if response.status_code == 200:
                data = response.json().get("leaderboard", [])
                if data:
                    # Save fresh data locally
                    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                    self.fetched.emit(data)
                    return
            self.failed.emit()
        except Exception:
            self.failed.emit()

class LeaderCard(QFrame):
    def __init__(self, username, points):
        super().__init__()
        self.setMinimumSize(80, 100)
        self.setStyleSheet("""
            background-color: transparent;
            border-radius: 18px;
        """)

        layout = QVBoxLayout(self);

        name_label = QLabel(username)
        name_label.setStyleSheet(f"color: {theme.text.name()}; font-size: 16px; font-weight: bold;")
        layout.addWidget(name_label);
        # name_label.setGeometry(0, 50, 140, 30)

        points_label = QLabel(f"Points: {points}")
        points_label.setStyleSheet(f"color: {theme.text.name()}; font-size: 14px;")
        layout.addWidget(points_label);
        # points_label.setGeometry(0, 90, 140, 25)

class Leaderboard(QWidget):
    def __init__(self):
        super().__init__()
        self.leaderboard_data = []
        self.setup_ui()
        # Start loading data: try fetch from server, fallback to local file
        self.start_fetch()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(5)

        self.header_label = QLabel("Leaderboard")
        self.header_label.setStyleSheet(f"color: {theme.text.name()}; font-size: 24px; font-weight: bold;")
        self.main_layout.addWidget(self.header_label)

        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout(self.top_widget)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(5)
        self.top_widget.setLayout(self.top_layout)
        self.main_layout.addWidget(self.top_widget)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.setStyleSheet(f"""
            background-color: {theme.background.name()};
            color: {theme.text.name()};
            border: none;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        """)
        self.search_input.textChanged.connect(self.filter_table)
        self.main_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rank", "Username", "Points"])
        self.table.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {theme.primary.name()};
                color: {theme.background.name()};
                padding: 8px;
                border: none;
            }}
            QTableWidget {{
                background-color: {theme.background.name()};
                color: {theme.text.name()};
                border: none;
                gridline-color: {theme.background_alternative.name()};
            }}
            QTableWidget::item {{
                padding: 6px;
            }}
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.main_layout.addWidget(self.table);

    def start_fetch(self):
        self.thread = FetchLeaderboardThread()
        self.thread.fetched.connect(self.on_fetch_success)
        self.thread.failed.connect(self.on_fetch_fail)
        self.thread.start()

    def on_fetch_success(self, data):
        self.leaderboard_data = data
        self.update_ui_with_data()

    def on_fetch_fail(self):
        # Try loading local file if fetch fails
        if os.path.exists(LOCAL_FILE):
            try:
                with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                    self.leaderboard_data = json.load(f)
                if self.leaderboard_data:
                    self.update_ui_with_data()
                    return
            except Exception as e:
                print("Error loading local leaderboard.json:", e)
        # If no local data, show error message
        self.show_empty_message()

    def update_ui_with_data(self):
        self.leaderboard_data.sort(key=lambda x: x.get("points", 0), reverse=True)
        self.populate_top_cards()
        self.populate_table()
        # self.top_scroll.show()
        self.table.show()
        self.search_input.setEnabled(True)

        # If error message label exists, remove it
        if hasattr(self, 'empty_label'):
            self.empty_label.hide()
            self.main_layout.removeWidget(self.empty_label)
            self.empty_label.deleteLater()
            del self.empty_label

    def show_empty_message(self):
        for i in reversed(range(self.top_layout.count())):
            widget = self.top_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.table.clearContents()
        self.table.setRowCount(0)
        self.search_input.setEnabled(False)
        self.top_scroll.hide()
        self.table.hide()

        self.empty_label = QLabel("Unable to load leaderboard at this time")
        self.empty_label.setStyleSheet(f"color: {theme.text.name()}; font-size: 18px; font-weight: bold;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.empty_label)

    def populate_top_cards(self):
        for i in reversed(range(self.top_layout.count())):
            widget = self.top_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        for user in self.leaderboard_data[:3]:
            card = LeaderCard(user.get("username", "N/A"), user.get("points", 0))
            self.top_layout.addWidget(card)

    def populate_table(self):
        self.table.setRowCount(len(self.leaderboard_data))
        for i, user in enumerate(self.leaderboard_data):
            rank_item = QTableWidgetItem(str(i + 1))
            username_item = QTableWidgetItem(user.get("username", "N/A"))
            points_item = QTableWidgetItem(str(user.get("points", 0)))

            for item in (rank_item, username_item, points_item):
                item.setForeground(Qt.GlobalColor.white)

            self.table.setItem(i, 0, rank_item)
            self.table.setItem(i, 1, username_item)
            self.table.setItem(i, 2, points_item)

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            username_item = self.table.item(row, 1)
            self.table.setRowHidden(row, not (username_item and text in username_item.text().lower()))
