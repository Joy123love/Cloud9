
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from ..editor.widget import CodeEditor
from theming.theme import theme


class CreateCodeEditor(QWidget):
    def __init__(self, start : str, solution : str, *args, **kwargs):
        super().__init__(*args, **kwargs);
        layout = QVBoxLayout();
        layout.setSpacing(0);
        layout.setContentsMargins(0,0,0,0)

        self.tab = QTabWidget();
        self.start_editor = CodeEditor(start);
        self.solution_editor = CodeEditor(solution);
        self.tab.addTab(self.start_editor, "Starting Point");
        self.tab.addTab(self.solution_editor, "Solution");
        self.tab.setStyleSheet(f"background: {theme.background_alternative.name()}; color : {theme.text.name()}")
        layout.addWidget(self.tab);
        

        self.setLayout(layout);
