import sys
from PyQt6.QtWidgets import QWidget
import subprocess
import os
import routes

class FlappyLearnScreen(QWidget):
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
        print(f"Launching Flappy Learn (from screen.py) at: {script_path}")
        id, _ = routes.get_user();
        subprocess.Popen([sys.executable, script_path, id]) 
