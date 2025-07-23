import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout




class SwitchRunnerScreen(QWidget):
    def __init__(self):
        super().__init__()

    def play(self):
        from .game import HEIGHT, WIDTH, SwitchRunnerGame
        import pygame
        self.setGeometry(100, 100, 800, 600)
        pygame.init()
        self.pygame_surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        handle = pygame.display.get_wm_info()['window']  
        self.pygame_window = QWindow.fromWinId(handle)
        self.pygame_widget = QWidget.createWindowContainer(self.pygame_window, self)  
        self.pygame_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus) 
        self.pygame_widget.setGeometry(0, 0, 640, 480)

        game = SwitchRunnerGame();
        game.run(self.pygame_surface);
