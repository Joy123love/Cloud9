import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow

app = QApplication(sys.argv)
win = LoginWindow()
win.show()
sys.exit(app.exec())
