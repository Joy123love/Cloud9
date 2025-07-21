from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QDockWidget, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QTabWidget, QTextEdit, QVBoxLayout, QWidget

from assets.icons import icons
from quizzes.details import QuizDetails
from widgets.text.line import LineTextEdit
from coding.editor.widget import font, theme

class SidebarTop(QWidget):
    def __init__(self, name : str, description : str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();

        self.name = LineTextEdit(name, font = font.heading, height = 50);
        self.name.setStyleSheet(f"color: {theme.secondary.name()}; background: {theme.background.name()};")
        layout.addWidget(self.name);

        self.description = QTextEdit(description);
        self.description.setFont(font.default);
        self.description.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background.name()};")
        self.description.setFixedHeight(150)
        layout.addWidget(self.description);
        
        self.setLayout(layout);

class Question(QWidget):
    def __init__(self, pos : int, text: str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QHBoxLayout();
        self.position = pos;

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background: {theme.background.name()}; border-radius: 10px; padding : 5px")

        self.input = LineTextEdit(text, color = theme.text);
        layout.addWidget(self.input);
        
        self.remove = QPushButton();
        self.remove.setIcon(icons.delete)
        layout.addWidget(self.remove);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

class SidebarBottom(QWidget):
    def __init__(self, questions : list[str], *args, **kwargs):
        super().__init__(*args, **kwargs);
        header_layout = QHBoxLayout();
        
        self.title = QLabel("Questions");
        self.title.setFont(font.default);
        self.title.setStyleSheet(f"color: {theme.primary.name()}")
        header_layout.addWidget(self.title);
        
        self.add = QPushButton();
        self.add.setIcon(icons.add)
        self.add.setStyleSheet(f"color: {theme.secondary.name()}; background-color: {theme.background.name()}")
        header_layout.addWidget(self.add);

        header = QWidget();
        header.setLayout(header_layout);

        layout = QVBoxLayout();
        layout.addWidget(header);

        for i, value in enumerate(questions):
            question =Question(i, value);
            # question.setFixedHeight(80);
            layout.addWidget(question, 0, Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout);


class CreateSidebar(QDockWidget):
    def __init__(self, details : QuizDetails, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setBackgroundRole(QPalette.ColorRole.Window);
        self.setAutoFillBackground(True);
        
        self.main = QWidget();
        layout = QVBoxLayout();
        self.top = SidebarTop(details.name, details.description);

        layout.addWidget(self.top);
        self.bottom = SidebarBottom(details.convert_to_list());
        self.bottom.setMinimumHeight(700);
        layout.addWidget(self.bottom);

        self.main.setLayout(layout)
        self.setWidget(self.main)

