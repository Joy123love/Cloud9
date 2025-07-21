import sys
from PyQt6.QtWidgets import QApplication
from signup_window import  SignUpWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignUpWindow()
    window.show()
    sys.exit(app.exec())
