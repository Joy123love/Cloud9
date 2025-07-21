from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QDockWidget, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QScrollArea, QVBoxLayout, QWidget

from coding.details import ChallengeDetails
from coding.editor.widget import font, theme

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

class Statement(QWidget):
    def __init__(self, key : str, amt : int, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.id = key;

        layout = QHBoxLayout();

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background: {theme.background.name()}; border-radius: 10px; padding : 5px")

        self.key = QLabel(key);
        self.key.setFont(font.small);
        self.key.setStyleSheet(f"color: {theme.primary.name()}")
        layout.addWidget(self.key);

        self.amt = QLabel(str(amt));
        self.amt.setFont(font.small);
        self.amt.setStyleSheet(f"color: {theme.text.name()}")
        layout.addWidget(self.amt);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

class SidebarBottom(QWidget):
    def __init__(self, statements : dict[str, int], *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)
        
        self.title = QLabel("Restricted Statements");
        self.title.setFont(font.default);
        self.title.setStyleSheet(f"color: {theme.primary.name()}")

        layout.addWidget(self.title);

        statements_layout = QVBoxLayout();
        for (key, value) in statements.items():
            statements_layout.addWidget(Statement(key, int(value)), 0, Qt.AlignmentFlag.AlignTop)

        self.statements = QWidget();
        self.statements.setLayout(statements_layout);

        statements_scroll = QScrollArea();
        statements_scroll.setWidget(self.statements);
        statements_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(statements_scroll);
        self.setLayout(layout);

class PlaySidebar(QDockWidget):
    def __init__(self, details : ChallengeDetails, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.main = QWidget();
        layout = QVBoxLayout();
        self.top = SidebarTop(details.name, details.username, details.description);

        layout.addWidget(self.top);
        self.bottom = SidebarBottom(details.statements);
        layout.addWidget(self.bottom);

        self.main.setLayout(layout)
        self.setWidget(self.main)

