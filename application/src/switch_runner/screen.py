import sys
from PyQt6.QtWidgets import QWidget
import subprocess
import os

class SwitchRunnerScreen(QWidget):
    def __init__(self):
        super().__init__()

    def play(self):
        # Launch the Pygame game as a separate process
        script_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "game.py"
            )
        )
        print(f"Launching Switch Runner (from screen.py) at: {script_path}")
        subprocess.Popen([sys.executable, script_path])
