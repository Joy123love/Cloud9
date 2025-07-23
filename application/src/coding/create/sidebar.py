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
    def __init__(self, pos : int, text: str, delete, *args, **kwargs):
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
        self.remove.mousePressEvent = lambda e: delete(pos)
        layout.addWidget(self.remove);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

class Statement(QWidget):
    def __init__(self, key : str, amt : int, delete, *args, **kwargs):
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
        
        self.remove = QPushButton();
        self.remove.setIcon(icons.delete)
        self.remove.mousePressEvent = lambda e: delete(key)
        layout.addWidget(self.remove);

        children = QWidget();
        children.setLayout(layout);
        layout = QVBoxLayout();
        layout.addWidget(children);
        self.setLayout(layout);

class SidebarBottomChecks(QWidget):
    def __init__(self, checks : list[str], add, delete, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        self.add = QPushButton();
        self.add.setIcon(icons.add);
        self.add.mousePressEvent = add
        layout.addWidget(self.add)
        self.checks : list[Check] = []
        
        for i, value in enumerate(checks):
            check = Check(i, value, delete);
            self.checks.append(check);
            layout.addWidget(check, 0, Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout);
    
    def get_checks(self) -> list[str]:
        checks : list[str] = [];
        for check in self.checks:
            checks.append(check.input.text());

        return checks;

class SidebarBottomStatements(QWidget):
    def __init__(self, statements : dict[str, int], add, delete, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        self.add = QPushButton();
        self.add.setIcon(icons.add);
        self.add.mousePressEvent = add
        self.statements : list[Statement] = []
        layout.addWidget(self.add)

        for (key, value) in statements.items():
            statement = Statement(key, int(value), delete)
            self.statements.append(statement)
            layout.addWidget(statement, 0, Qt.AlignmentFlag.AlignTop)

        self.setLayout(layout);

    def get_statements(self) -> dict[str, int]:
        statements : dict[str, int] = {};
        for statement in self.statements:
            statements[statement.key.text()] = int(statement.amt.text())

        return statements;


class SidebarBottom(QWidget):
    def __init__(self, statements : dict[str, int], checks : list[str], add_statement, add_check, delete_statement, delete_check, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        self.tab = QTabWidget();
        self.statements = SidebarBottomStatements(statements, add_statement, delete_statement);
        self.checks = SidebarBottomChecks(checks, add_check, delete_check);
        
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
        self.mlayout = QVBoxLayout();
        self.top = SidebarTop(self.details.name, self.details.description);
        self.mlayout.addWidget(self.top);

        self.bottom = SidebarBottom(self.details.statements, self.details.checks, add_statement=self.new_statement, add_check=self.new_check, delete_check=self.delete_check, delete_statement=self.delete_statement);
        self.mlayout.addWidget(self.bottom);

        self.main.setLayout(self.mlayout)
        self.setWidget(self.main)

    def new_statement(self, _e):
        self.details.statements = self.bottom.statements.get_statements();
        self.details.statements["new"] = 10;
        self.reload_details();
        self.update()
    
    def delete_statement(self, key : str):
        self.details.statements = self.bottom.statements.get_statements();
        self.details.statements.pop(key);
        self.reload_details();
        self.update()

    def reload_details(self):
        index = self.bottom.tab.currentIndex();
        self.bottom.close();
        self.bottom = SidebarBottom(self.details.statements, self.details.checks, add_statement=self.new_statement, add_check=self.new_check, delete_check=self.delete_check, delete_statement=self.delete_statement);
        self.mlayout.addWidget(self.bottom);
        self.bottom.tab.setCurrentIndex(index);
    
    def new_check(self, _e):
        self.details.checks = self.bottom.checks.get_checks();
        self.details.checks.append("new");
        self.reload_details();
        self.update()

    def delete_check(self, index : int):
        self.details.checks = self.bottom.checks.get_checks();
        self.details.checks.pop(index);
        self.reload_details();
        self.update()


