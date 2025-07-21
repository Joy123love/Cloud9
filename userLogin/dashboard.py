from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
import requests


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.load_button = QPushButton("Load Leaderboard")
        self.load_button.clicked.connect(self.load_leaderboard)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rank", "Username", "Points"])
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 100)

        layout.addWidget(self.load_button)
        layout.addWidget(self.table)

    def load_leaderboard(self):
        try:
            response = requests.get("http://127.0.0.1:5000/leaderboard")
            if response.status_code == 200:
                leaderboard = response.json().get("leaderboard", [])
                self.table.setRowCount(len(leaderboard))

                for index, entry in enumerate(leaderboard):
                    rank_item = QTableWidgetItem(str(index + 1))
                    user_item = QTableWidgetItem(entry.get("username", "N/A"))
                    points_item = QTableWidgetItem(str(entry.get("points", 0)))

                    self.table.setItem(index, 0, rank_item)
                    self.table.setItem(index, 1, user_item)
                    self.table.setItem(index, 2, points_item)

            else:
                QMessageBox.warning(self, "Error", "Failed to fetch leaderboard.")
        except Exception as e:
            print("Leaderboard error:", e)
            QMessageBox.critical(self, "Error", "Could not connect to server.")
