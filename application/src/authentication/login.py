from collections.abc import Callable
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QWidget, QGridLayout, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
import os
import requests
import routes
# from dashboard import DashboardWindow

from assets.icons import icons
from .styles import STYLES

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.open_signup : Callable[[], None]|None = None;
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # === LEFT PANEL ===
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #3AA9AD, stop:1 red);
            border-top-left-radius: 10px;
            border-bottom-left-radius: 10px;
        """)

        left_layout = QVBoxLayout(left_panel)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.setContentsMargins(40, 40, 40, 40)

        title_label = QLabel("Sign Up")
        title_label.setStyleSheet(STYLES["titleText"] + "; background: transparent;")
        title_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        description = QLabel("Enter your personal info and create new account")
        description.setStyleSheet(STYLES["normalText"]  + "; background: transparent;")
        description.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        sign_up_btn = QPushButton("Sign Up")
        sign_up_btn.setStyleSheet(STYLES["button"])
        sign_up_btn.clicked.connect(self.handle_open_signup)

        left_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop)
        left_layout.addSpacing(20)
        left_layout.addWidget(description)
        left_layout.addSpacing(50)
        left_layout.addWidget(sign_up_btn)

        # === RIGHT PANEL ===
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            background-color: white;
            border-top-right-radius: 10px;
            border-bottom-right-radius: 10px;
        """)

        right_layout = QVBoxLayout(right_panel)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.setContentsMargins(0, 0, 0, 0)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        top_bar.addStretch()


        close_btn = QPushButton()
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(QtGui.QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("border: none;")

        close_btn.setIcon(QIcon(icons.cancel))
        close_btn.setIconSize(QSize(20, 20))

        close_btn.clicked.connect(self.close)

        top_bar.addWidget(close_btn)
        right_layout.addLayout(top_bar)

        signin_title = QLabel("Sign in to App")
        signin_title.setStyleSheet(STYLES["titleText"])

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(STYLES["textBox"])

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(STYLES["textBox"])

        signin_btn = QPushButton("Sign In")
        signin_btn.setStyleSheet(STYLES["mainbutton"])
        signin_btn.clicked.connect(self.handle_sign_in)

        right_layout.addWidget(signin_title, alignment=Qt.AlignmentFlag.AlignTop)
        right_layout.addSpacing(30)
        right_layout.addWidget(self.email_input)
        right_layout.addSpacing(40)
        right_layout.addWidget(self.password_input)
        right_layout.addSpacing(60)
        right_layout.addWidget(signin_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(left_panel, 0, 0)
        layout.addWidget(right_panel, 0, 1)
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 3)

    def handle_open_signup(self):
        if routes.open_signup:
            routes.open_signup()

    def handle_sign_in(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter both email and password.")
            return

        try:
            from constants import SERVER_URL
            response = requests.post(
                SERVER_URL + "login",
                json={"email": email, "password": password},
                timeout=5
            )
            if response.status_code == 200:
                QtWidgets.QMessageBox.information(self, "Success", "Logged in successfully!")
                from main import window
                window.screens.open_signup_screen();
                if routes.open_dashboard:
                    routes.open_dashboard()
            else:
                msg = response.json().get('message', 'Login failed.')
                QtWidgets.QMessageBox.warning(self, "Failed", msg)
        except Exception as e:
            print("Login error:", e)
            QtWidgets.QMessageBox.warning(self, "Error", "Could not connect to server.")
