from PyQt6.QtCore import Qt
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from backend.dashboard.notepad_db import init_db, add_file_to_db, get_all_files, delete_file_from_db
from assets import icons
from theming.theme import theme


class FileRow(QFrame):
    def __init__(self, filename : str, delete_file, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setMinimumHeight(56)
        self.setStyleSheet(f'background-color: {theme.background.name()}; border-radius: 12px;')
        file_row = QHBoxLayout(self)
        file_row.setContentsMargins(0, 0, 10, 0)
        file_row.setSpacing(0)
        
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet("QCheckBox { margin-left: 12px; margin-right: 8px; } QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; background: "+theme.background_alternative.name()+"; border: 1.5px solid " + theme.background.name() + "; } QCheckBox::indicator:checked { background: " + theme.primary.name() + ";}")
        file_row.addWidget(self.checkbox)
        
        file_label = QLabel(filename)
        file_label.setStyleSheet('color: #fff; font-size: 16px; font-weight: bold; padding-left: 18px; background: transparent; border: none;')
        file_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        file_row.addWidget(file_label)
        file_row.addStretch(1)
        
        def get_icon(path : str) -> QSvgWidget:
            icon = QSvgWidget(path)
            icon.setFixedSize(24, 24)
            icon.setStyleSheet('background: transparent; border: none')
            return icon

        edit_icon = get_icon(icons.get_path('edit.svg'))
        edit_icon.setStyleSheet('background: transparent; border: none; margin-right: 18px;')
        file_row.addWidget(edit_icon)
        file_row.addSpacing(10)
        
        self.delete_icon = get_icon(icons.get_path('delete.svg'))
        self.delete_icon.mousePressEvent = lambda e, fn=filename: delete_file(fn)
        file_row.addWidget(self.delete_icon)

        self.setLayout(file_row)


class DashboardFiles(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);
        self.file_rects : list[FileRow] = []
        self.file_checkboxes = []
        self.file_list_layout = QVBoxLayout()
        self.setLayout(self.file_list_layout);
        self.file_list_layout.setSpacing(5)
        self.search_query = None;
        self.selected_files = set()
    
    def on_search_text_changed(self, text):
        self.search_query = text
        self.refresh_file_list()

    def refresh_file_list(self):
        self.file_rects.clear()
        self.file_checkboxes.clear()

        while self.file_list_layout.count():
            item = self.file_list_layout.takeAt(0)
            if not item:
                continue;
            widget = item.widget()
            if widget:
                widget.deleteLater()
        file_names = get_all_files()
        
        # Filter files by search query
        if self.search_query:
            file_names = [fn for fn in file_names if self.search_query in fn.lower()]

        for filename in file_names:
            file_rect = FileRow(filename, self.delete_file);
            self.file_rects.append(file_rect)
            self.file_list_layout.addWidget(file_rect)

        # self.files_layout.addLayout(self.file_list_layout)

    def delete_file(self, filename):
        import os;
        delete_file_from_db(filename)
        file_path = os.path.join('jsons', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.refresh_file_list()

    def enter_selection_mode(self):
        self.selection_mode = True
        for i, file in enumerate(self.file_rects):
            file.checkbox.setVisible(True)
            file.checkbox.setChecked(False)
        self.update()

    def exit_selection_mode(self):
        self.selection_mode = False
        for i, file in enumerate(self.file_rects):
            file.checkbox.setVisible(False)
            file.checkbox.setChecked(False)
        self.update()

    def select_all_files(self):
        for i, file in enumerate(self.file_rects):
            file.checkbox.setChecked(True)
        self.update()

    def delete_selected_files(self):
        file_names = get_all_files()
        for idx, file in enumerate(self.file_rects):
            if file.checkbox.isChecked():
                filename = file_names[idx]
                self.delete_file(filename)
        self.exit_selection_mode()

    def toggle_select_all_files(self):
        file_count = len(self.file_rects)
        all_selected = all(file.checkbox.isChecked() for file in self.file_rects) and file_count > 0
        for file in self.file_rects:
            file.checkbox.setChecked(not all_selected)

        self.update()
