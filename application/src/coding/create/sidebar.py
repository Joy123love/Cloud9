from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QDockWidget, QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QScrollArea, QTabWidget, QTextEdit, QVBoxLayout, QWidget

from assets.icons import icons
from widgets.text.line import LineTextEdit

from coding.editor.widget import font, theme
from coding.details import ChallengeDetails

class SidebarTop(QWidget):
    def __init__(self, name : str, description : str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();

        self.name = LineTextEdit(name, font = font.heading, height = 50);
        self.name.setStyleSheet(f"color: {theme.secondary.name()}; background: {theme.background_alternative.name()};")
        layout.addWidget(self.name);

        self.description = QTextEdit(description);
        self.description.setFont(font.default);
        self.description.setStyleSheet(f"color: {theme.text.name()}; background: {theme.background_alternative.name()};")
        self.description.setFixedHeight(150)
        layout.addWidget(self.description);
        
        self.setLayout(layout);

class Check(QWidget):
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

class Statement(QWidget):
    def __init__(self, key : str, amt : int, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QHBoxLayout();
        self.id = key;

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True)
        self.setStyleSheet(f"background: {theme.background.name()}; border-radius: 10px; padding : 5px")

        self.key = LineTextEdit(key, color = theme.primary);
        layout.addWidget(self.key);

        self.amt = LineTextEdit(str(amt), color = theme.text);
        layout.addWidget(self.amt);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

class SidebarBottomChecks(QWidget):
    def __init__(self, checks : list[str], *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        for i, value in enumerate(checks):
            layout.addWidget(Check(i, value), 0, Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout);

class SidebarBottomStatements(QWidget):
    def __init__(self, statements : dict[str, int], *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        for (key, value) in statements.items():
            layout.addWidget(Statement(key, int(value)), 0, Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout);

class SidebarBottom(QWidget):
    def __init__(self, statements : dict[str, int], checks : list[str], *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        self.tab = QTabWidget();
        self.statements = SidebarBottomStatements(statements);
        self.checks = SidebarBottomChecks(checks);
        
        statements_scroll = QScrollArea();
        statements_scroll.setWidget(self.statements);
        statements_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab.addTab(statements_scroll, "Restricted Statements");

        checks_scroll = QScrollArea();
        checks_scroll.setWidget(self.checks)
        checks_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.tab.addTab(checks_scroll, "Checks");

        self.tab.setStyleSheet(f"background: {theme.background_alternative.name()}; color : {theme.text.name()}")
        layout.addWidget(self.tab);
        

        self.setLayout(layout);


class CreateSidebar(QDockWidget):
    def __init__(self, details : ChallengeDetails, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.details = details;

        self.main = QWidget();
        layout = QVBoxLayout();
        self.top = SidebarTop(self.details.name, self.details.description);

        layout.addWidget(self.top);
        self.bottom = SidebarBottom(self.details.statements, self.details.checks);
        layout.addWidget(self.bottom);

        self.main.setLayout(layout)
        self.setWidget(self.main)

    def new_statement(self):
        self.details.statements["new"] = 100000;



