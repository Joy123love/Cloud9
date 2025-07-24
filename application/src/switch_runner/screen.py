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
#         from .game import HEIGHT, WIDTH, SwitchRunnerGame
#         import pygame
#         self.setGeometry(100, 100, 1280, 720)
#         pygame.init()
#         self.pygame_surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
#         handle = pygame.display.get_wm_info()['window']  
#         self.pygame_window = QWindow.fromWinId(handle)
#         self.pygame_widget = QWidget.createWindowContainer(self.pygame_window, self)  
#         self.pygame_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 
#         self.pygame_widget.setGeometry(0, 0, 1280, 720)
#
#         game = SwitchRunnerGame();
#         game.run(self.pygame_surface);
# >>>>>>> Stashed changes
