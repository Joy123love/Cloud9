import sys
import pygame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QWindow
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from .game import HEIGHT, WIDTH, run


class SwitchRunnerScreen(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("Pygame and PyQt Example")
        self.setGeometry(100, 100, 800, 600)
        # Create a Pygame surface and pass it to a QWindow
        pygame.init()
        pygame.display.set_caption("Pygame Window")
        self.pygame_surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
        handle = pygame.display.get_wm_info()['window']  # Get the handle to the Pygame window
        self.pygame_window = QWindow.fromWinId(handle)  # Create a QWindow from the handle
        self.pygame_widget = QWidget.createWindowContainer(self.pygame_window, self)  # Create a QWidget using the QWindow
        self.pygame_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Set the focus policy of the QWidget
        self.pygame_widget.setGeometry(0, 0, 640, 480)  # Set the size and position of the QtWidgets

        # Add the Pygame widget to the main window
        layout = QVBoxLayout()
        layout.addWidget(self.pygame_widget)
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        run(self.pygame_surface);
