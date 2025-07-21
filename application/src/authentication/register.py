from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QWidget

from theming.theme import theme
from widgets.text.line import LineTextEdit
from theming.font import font


class RegisterScreen(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();

        self.username = LineTextEdit(placeholder = "Enter Username", font = font.default, height = 50);
        self.username.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background_alternative.name()}; border-radius: 10px; padding : 15pxl width : 400px")
        layout.addWidget(self.username, 0, Qt.AlignmentFlag.AlignCenter);
        
        self.email = LineTextEdit(placeholder = "Enter Email",font = font.default, height = 50);
        self.email.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background_alternative.name()}; border-radius: 10px; padding : 15pxl width : 400px")
        layout.addWidget(self.username, 0, Qt.AlignmentFlag.AlignCenter);
        
        self.password = LineTextEdit(placeholder = "Enter Password",font = font.heading, height = 50);
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background_alternative.name()}; border-radius: 10px; padding : 5px")
        layout.addWidget(self.password, 0, Qt.AlignmentFlag.AlignCenter);
        
        self.confirm = LineTextEdit(placeholder = "Confirm Password",font = font.heading, height = 50);
        self.confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background_alternative.name()}; border-radius: 10px; padding : 5px")
        layout.addWidget(self.password, 0, Qt.AlignmentFlag.AlignCenter);
        
        button_layout = QHBoxLayout();

        self.login = QPushButton("login");
        self.login.setFont(font.default);
        self.login.setStyleSheet(f"color: {theme.background.name()}; background: {theme.secondary.name()}; border-radius: 10px; padding : 10px; width : 100px")
        button_layout.addWidget(self.login, 0, Qt.AlignmentFlag.AlignHCenter);
        
        self.register = QPushButton("register");
        self.register.setFont(font.default);
        self.register.setStyleSheet(f"color: {theme.background.name()}; background: {theme.primary.name()}; border-radius: 10px; padding : 10px; width :100px")
        button_layout.addWidget(self.register, 0, Qt.AlignmentFlag.AlignHCenter);

        button_layout.setDirection(QHBoxLayout.Direction.LeftToRight);
        buttons = QWidget();
        buttons.setLayout(button_layout);

        layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignCenter);

        self.setLayout(layout);
