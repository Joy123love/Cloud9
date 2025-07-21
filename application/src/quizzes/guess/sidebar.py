from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QDockWidget, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QScrollArea, QSpacerItem, QVBoxLayout, QWidget

from coding.editor.widget import font, theme
from quizzes.details import QuizDetails



class SidebarTop(QWidget):
    def __init__(self, name : str, username : str, description : str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();

        self.name = QLabel(name);
        self.name.setFont(font.heading);
        self.name.setStyleSheet(f"color: {theme.secondary.name()}")
        layout.addWidget(self.name);

        self.username = QLabel(username);
        self.username.setFont(font.default);
        self.username.setStyleSheet(f"color: {theme.primary.name()}")
        layout.addWidget(self.username);

        self.description = QLabel(description);
        self.description.setFont(font.default);
        self.description.setStyleSheet(f"color: {theme.text.name()}")
        layout.addWidget(self.description);
        
        self.setLayout(layout);

class Question(QWidget):
    def __init__(self, pos : int, text: str,*args, **kwargs):
        super().__init__(*args, **kwargs);
        self.position = pos;

        layout = QHBoxLayout();

        # self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"border-radius: 10px; padding : 25px; border-width : 1px; border-color : {theme.background_alternative.name()}; border-style : solid")

        self.key = QLabel(text);
        self.key.setFont(font.default);
        self.key.setStyleSheet(f"color: {theme.text.name()}")
        layout.addWidget(self.key);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

class SidebarBottom(QWidget):
    def __init__(self, questions : list[str], *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)
        
        self.title = QLabel("Questions");
        self.title.setFont(font.default);
        self.title.setStyleSheet(f"color: {theme.primary.name()}")

        layout.addWidget(self.title);

        statements_layout = QVBoxLayout();
        for (i, value) in enumerate(questions):
            statements_layout.addWidget(Question(i, value), 0, Qt.AlignmentFlag.AlignTop)

        self.statements = QWidget();
        self.statements.setLayout(statements_layout);

        statements_scroll = QScrollArea();
        statements_scroll.setWidget(self.statements);
        statements_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(statements_scroll);
        self.setLayout(layout);

class GuessSidebar(QDockWidget):
    def __init__(self, details : QuizDetails, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setBackgroundRole(QPalette.ColorRole.Window);
        self.setAutoFillBackground(True);
        
        self.main = QWidget();
        layout = QVBoxLayout();
        
        self.top = SidebarTop(details.name, details.username, details.description);
        layout.addWidget(self.top);

        self.bottom = SidebarBottom(details.convert_to_list());
        layout.addWidget(self.bottom);

        self.main.setLayout(layout)
        self.setWidget(self.main)
