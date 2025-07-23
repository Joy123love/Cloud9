from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QSizePolicy, QWidget

from theming.theme import theme
from assets import icons


class DashboardSearchbar(QWidget):
    def __init__(self, on_search_text_changed, *args, **kwargs):
        super().__init__(*args, **kwargs);
        
        self.file_rects = []
        self.file_checkboxes = []
        self.selection_mode = False

        self.search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search files...')
        self.search_box.setMinimumWidth(400)
        self.search_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_box.setStyleSheet("QLineEdit { background: " + theme.background_alternative.name() +"; color: " + theme.text.name() + "; border-radius: 10px; border: 1px solid " + theme.background.name() + "; padding: 8px 16px; font-size: 15px; margin-bottom: 0px; } QLineEdit:focus { border: 1px solid " + theme.text.name() + "; }")
        self.search_box.textChanged.connect(on_search_text_changed)
        self.setLayout(self.search_row);
