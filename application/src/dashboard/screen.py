import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QStackedWidget, QLineEdit, QCheckBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage, QLinearGradient, QBrush, QPen, QPainterPath
from PyQt6.QtCore import QRectF
from PyQt6.QtSvgWidgets import QSvgWidget
import re
import os
from functools import partial
import subprocess
from backend.dashboard.notepad_db import init_db, add_file_to_db, get_all_files, delete_file_from_db
from assets import icons
from utils import get_project_root

# Custom BannerFrame for scaled background image and overlay
class BannerFrame(QFrame):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.setMinimumHeight(120)
        # self.setMaximumHeight(220)
        self.setStyleSheet('border-radius: 16px;')

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        # Clip to rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 16, 16)
        painter.setClipPath(path)
        # Draw scaled background image
        if not self.pixmap.isNull():
            scaled = self.pixmap.scaled(rect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(rect, scaled, scaled.rect())
        # Draw semi-transparent overlay
        overlay_color = QColor(20, 30, 50, int(255 * 0.45))  # 45% opacity dark overlay
        painter.setBrush(overlay_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)
        super().paintEvent(event)

class SidebarFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(80)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        radius = 20
        # Gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor('#3A6DB1'))
        gradient.setColorAt(1, QColor('#25467B'))
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(QPen(QColor('#e0e0e0'), 1))
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), radius, radius)

class DashboardScreen(QWidget):
    def __init__(self, username="Guest"):
        super().__init__()
        # self.setWindowTitle('Gaming Dashboard')
        self.setGeometry(100, 100, 1200, 700)
        self.setAutoFillBackground(True);
        self.setStyleSheet('background-color: #152E57;')  # Darker background for main window
        self.username = username
        self.selected_sidebar_index = 0  # 0: Home, 1: File Plus, 2: Settings
        self.sidebar_icons = []
        self.selection_mode = False
        self.selected_files = set()
        self.file_rects = []
        self.file_checkboxes = []
        init_db()
        self.files_layout = QVBoxLayout()  # Ensure this is always defined
        self.init_ui()
        self.refresh_file_list()  # Always show files from the database on startup

    def init_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Sidebar with gradient background
        sidebar = SidebarFrame()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.addStretch()
        # Sidebar icons with state management
        home_icon = QSvgWidget(icons.get_path("home-tinted.svg"));
        home_icon.setFixedSize(32, 32)
        home_icon.setStyleSheet('background: transparent;')
        file_plus_icon = QSvgWidget(icons.get_path("file-plus-outline.svg"));
        file_plus_icon.setFixedSize(32, 32)
        file_plus_icon.setAutoFillBackground(True);
        file_plus_icon.setStyleSheet('background: transparent;')
        settings_icon = QSvgWidget(icons.get_path("settings-outline.svg"));
        settings_icon.setFixedSize(32, 32)
        settings_icon.setStyleSheet('background: transparent;')
        self.sidebar_icons = [home_icon, file_plus_icon, settings_icon]
        # Add click event handling
        
        for idx, icon_widget in enumerate(self.sidebar_icons):
            icon_widget.mousePressEvent = partial(self.sidebar_icon_clicked, idx)
        
        # Icon group
        icon_group = QVBoxLayout()
        icon_group.setSpacing(28)
        icon_group.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for icon_widget in self.sidebar_icons:
            icon_group.addWidget(icon_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addLayout(icon_group)
        sidebar_layout.addStretch()
        self.update_sidebar_icons()

        # Main content area (now inside a vertical scroll area)
        # QStackedWidget for main content area
        self.content_stack = QStackedWidget()
        # Home page (current dashboard)
        home_inner = QFrame()
        home_inner.setStyleSheet('background: transparent; border-radius: 20px;')
        home_layout = QVBoxLayout(home_inner)
        # Add greeting and popular games as before
        greeting_frame = BannerFrame(os.path.join('assets', 'images', 'banner2.jpeg'))
        greeting_layout = QVBoxLayout(greeting_frame)
        greeting_layout.setContentsMargins(32, 16, 32, 16)
        greeting_label = QLabel(f'Hello, {self.username}')
        greeting_label.setStyleSheet('color: #ffffff; font-size: 24px; font-weight: bold; background: transparent;')
        greeting_sub = QLabel('Welcome back to our platform')
        greeting_sub.setStyleSheet('color: #b0c4de; font-size: 14px; background: transparent;')
        greeting_layout.addWidget(greeting_label)
        greeting_layout.addWidget(greeting_sub)
        home_layout.addWidget(greeting_frame)
        popular_label = QLabel('Popular Games')
        popular_label.setStyleSheet('color: #ffffff; font-size: 15px; font-weight: bold; margin-top: 24px; margin-bottom: 0px;')
        home_layout.addWidget(popular_label)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet('background: transparent; border: none; QScrollBar:horizontal {height:0px;}')
        scroll_area.setFixedHeight(180)
        scroll_content = QFrame()
        scroll_content.setStyleSheet('background: transparent;')
        scroll_layout = QHBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(24)
        for i in range(6):
            card = QFrame()
            card.setFixedSize(140, 160)
            card.setStyleSheet('background-color: rgba(117,178,222,0.15); border-radius: 18px;')
            card_label = QLabel(f'Game {i+1}', card)
            card_label.setStyleSheet('color: #fff; font-size: 16px; font-weight: bold;')
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setGeometry(0, 60, 140, 40)
            scroll_layout.addWidget(card)
        scroll_area.setWidget(scroll_content)
        home_layout.addWidget(scroll_area)
        # Add 'Games' section (grid list)
        games_label = QLabel('Games')
        games_label.setStyleSheet('color: #ffffff; font-size: 15px; font-weight: bold; margin-top: 24px; margin-bottom: 8px;')
        home_layout.addWidget(games_label)
        from PyQt6.QtWidgets import QGridLayout, QSizePolicy
        games_grid = QGridLayout()
        games_grid.setSpacing(28)
        games_grid.setContentsMargins(0, 0, 0, 0)
        num_columns = 3
        for i in range(12):
            vcard = QFrame()
            vcard.setMinimumSize(140, 220)
            vcard.setMaximumSize(300, 300)
            vcard.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            vcard.setStyleSheet('background-color: rgba(117,178,222,0.10); border-radius: 14px;')
            vcard_label = QLabel(f'Game {i+7}', vcard)
            vcard_label.setStyleSheet('color: #fff; font-size: 15px; font-weight: bold;')
            vcard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vcard_label.setGeometry(0, 100, 140, 40)
            row = i // num_columns
            col = i % num_columns
            games_grid.addWidget(vcard, row, col)
        for col in range(num_columns):
            games_grid.setColumnStretch(col, 1)
        home_layout.addLayout(games_grid)
        home_layout.addStretch()
        # Wrap the home_inner in a vertical scroll area
        home_scroll = QScrollArea()
        home_scroll.setWidgetResizable(True)
        home_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        home_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        home_scroll.setStyleSheet('background: transparent; border: none;')
        home_scroll.setWidget(home_inner)
        # Files page (placeholder)
        files_frame = QFrame()
        files_frame.setStyleSheet('background: transparent; border-radius: 20px;')
        files_layout = QVBoxLayout(files_frame)
        files_label = QLabel('Files')
        files_label.setStyleSheet('color: #fff; font-size: 22px; font-weight: bold; margin-top: 32px;')
        files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        files_layout.addWidget(files_label)
        # Search bar and action icons row (dynamic)
        self.search_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText('Search files...')
        self.search_box.setMinimumWidth(400)
        self.search_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.search_box.setStyleSheet('QLineEdit { background: #22304a; color: #fff; border-radius: 10px; border: 1px solid #25467B; padding: 8px 16px; font-size: 15px; margin-bottom: 0px; } QLineEdit:focus { border: 1.5px solid #4fd1ff; }')
        self.search_box.textChanged.connect(self.on_search_text_changed)
        files_layout.addLayout(self.search_row)
        # Placeholder file list
        self.file_list_layout = QVBoxLayout()
        self.file_list_layout.setSpacing(18)
        self.file_rects.clear()
        self.file_checkboxes.clear()
        for i in range(6):
            file_rect = QFrame()
            file_rect.setMinimumHeight(56)
            file_rect.setStyleSheet('background-color: #12284D; border-radius: 12px; border: 0.5px solid #fff;')
            file_row = QHBoxLayout(file_rect)
            file_row.setContentsMargins(0, 0, 10, 0)
            file_row.setSpacing(0)
            # Checkbox (hidden by default)
            checkbox = QCheckBox()
            checkbox.setStyleSheet('QCheckBox { margin-left: 12px; margin-right: 8px; } QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; background: #22304a; border: 1.5px solid #b0b0b0; } QCheckBox::indicator:checked { background: #4fd1ff; border: 1.5px solid #4fd1ff; }')
            checkbox.setVisible(self.selection_mode)
            file_row.addWidget(checkbox)
            self.file_checkboxes.append(checkbox)
            file_label = QLabel(f'File {i+1}')
            file_label.setStyleSheet('color: #fff; font-size: 16px; font-weight: bold; padding-left: 18px; background: transparent; border: none;')
            file_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            file_row.addWidget(file_label)
            file_row.addStretch(1)
            edit_icon = QSvgWidget(icons.get_path("edit.svg"));
            edit_icon.setFixedSize(24, 24)
            edit_icon.setStyleSheet('background: transparent; border: none; margin-right: 18px;')
            file_row.addWidget(edit_icon)
            file_row.addSpacing(10)
            delete_icon = QSvgWidget(icons.get_path("delete.svg"));
            delete_icon.setFixedSize(24, 24)
            delete_icon.setStyleSheet('background: transparent; border: none;')
            delete_icon.setVisible(True)
            delete_icon.mousePressEvent = lambda e, fn=f'File {i+1}.json': self.delete_file(fn)
            file_row.addWidget(delete_icon)
            self.file_rects.append((file_rect, delete_icon, checkbox))
            self.file_list_layout.addWidget(file_rect)
        files_layout.addLayout(self.file_list_layout)
        self.update_search_row_icons()
        files_layout.addStretch()
        # Settings page (placeholder)
        settings_frame = QFrame()
        settings_frame.setStyleSheet('background: transparent; border-radius: 20px;')
        settings_layout = QVBoxLayout(settings_frame)
        settings_label = QLabel('Settings Section')
        settings_label.setStyleSheet('color: #fff; font-size: 22px; font-weight: bold; margin-top: 32px;')
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(settings_label)
        settings_layout.addStretch()
        # Add pages to stack
        self.content_stack.addWidget(home_scroll)
        self.content_stack.addWidget(files_frame)
        self.content_stack.addWidget(settings_frame)
        # Set default page to Home
        self.content_stack.setCurrentIndex(0)
        # Add the stack to the main layout as a widget
        # main_layout.addWidget(self.content_stack, stretch=2) # This line is removed

        # Right panel
        right_panel = QFrame()
        right_panel.setFixedWidth(300)
        right_panel.setStyleSheet('background-color: #12284D; border-radius: 20px;')
        right_panel_layout = QVBoxLayout(right_panel)
        # User profile section
        profile_container = QVBoxLayout()
        profile_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        from PyQt6.QtWidgets import QSpacerItem, QSizePolicy
        profile_container.addSpacerItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        # Top row: notification icon, name, profile pic
        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        # Notification icon
        # Load and tint notification icon SVG to white
        notif_icon = QSvgWidget(icons.get_path("notifications-tinted.svg"));
        notif_icon.setFixedSize(28, 28)
        notif_icon.setStyleSheet('background: transparent; margin-right: 8px;')
        # User name
        user_name = QLabel(self.username if self.username != "Guest" else "Guest")
        user_name.setStyleSheet('color: #fff; font-size: 15px; font-weight: bold; padding: 0 12px;')
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Profile picture (circle placeholder)
        profile_pic = QLabel()
        profile_pic.setFixedSize(60, 60)
        profile_pic.setStyleSheet('background-color: #25467B; border-radius: 30px; border: 2px solid #75B2DE;')
        profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add to top row in new order
        top_row.addWidget(notif_icon)
        top_row.addStretch(1)
        top_row.addWidget(user_name)
        top_row.addStretch(1)
        top_row.addWidget(profile_pic)
        profile_container.addLayout(top_row)
        # Rank label below
        user_rank = QLabel('Rank: Grandmaster')
        user_rank.setStyleSheet('color: #b0c4de; font-size: 13px; margin-top: 8px;')
        user_rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_container.addWidget(user_rank)
        profile_container.addSpacing(18)
        right_panel_layout.addLayout(profile_container)
        right_panel_layout.addStretch()

        # Add widgets to main layout in correct order
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content_stack, stretch=2)
        main_layout.addWidget(right_panel)

        self.setLayout(main_layout)

    def update_sidebar_icons(self):
        icon_paths = [
            ("home-tinted.svg", "home-outline.svg"),
            ("file-plus-tinted.svg", "file-plus-outline.svg"),
            ("settings-tinted.svg", "settings-outline.svg"),
        ]
        for i, icon_widget in enumerate(self.sidebar_icons):
            selected_path, unselected_path = icon_paths[i]
            icon_widget.load(icons.get_path(selected_path if self.selected_sidebar_index == i else unselected_path))

    def sidebar_icon_clicked(self, idx, event):
        self.selected_sidebar_index = idx
        self.update_sidebar_icons()
        self.content_stack.setCurrentIndex(idx)

    def update_search_row_icons(self):
        # Clear the search row
        while self.search_row.count():
            item = self.search_row.takeAt(0)
            if not item:
                continue
            widget = item.widget()
            # Only delete icons, not the persistent search box
            if widget and widget is not self.search_box:
                widget.deleteLater()
        self.search_row.addWidget(self.search_box)
        self.search_row.addStretch(1)
        file_count = len(self.file_rects)
        if not self.selection_mode:
            # Normal mode: select and add-file icons
            if file_count > 0:
                select_icon = QSvgWidget(icons.get_path("select.svg"));
                select_icon.setFixedSize(28, 28);
                select_icon.setStyleSheet('background: transparent; margin-right: 10px;')
                select_icon.mousePressEvent = lambda e: self.enter_selection_mode()
                self.search_row.addWidget(select_icon)
            add_file_icon = QSvgWidget(icons.get_path("add-file.svg"));
            add_file_icon.setFixedSize(28, 28)
            add_file_icon.setStyleSheet('background: transparent; margin-right: 20px;')
            add_file_icon.mousePressEvent = lambda e: self.open_add_file_dialog()
            self.search_row.addWidget(add_file_icon)
        else:
            # Selection mode: x, select-all/deselect-all, delete icons
            x_icon = QSvgWidget(icons.get_path("x.svg"))
            x_icon.setFixedSize(28, 28)
            x_icon.setStyleSheet('background: transparent; margin-right: 10px;')
            x_icon.mousePressEvent = lambda e: self.exit_selection_mode()
            # Determine if all files are selected
            all_selected = all(cb.isChecked() for _, _, cb in self.file_rects) and file_count > 0
            select_all_icon = QSvgWidget(icons.get_path('deselect-all.svg' if all_selected else 'select-all.svg'))
            select_all_icon.setFixedSize(28, 28)
            select_all_icon.setStyleSheet('background: transparent; margin-right: 10px;')
            select_all_icon.mousePressEvent = lambda e: self.toggle_select_all_files()
            delete_icon = QSvgWidget(icons.get_path('delete.svg'))
            delete_icon.setFixedSize(28, 28)
            delete_icon.setStyleSheet('background: transparent; margin-right: 20px;')
            delete_icon.mousePressEvent = lambda e: self.delete_selected_files()
            self.search_row.addWidget(x_icon)
            self.search_row.addWidget(select_all_icon)
            self.search_row.addWidget(delete_icon)
        self.search_row.update()

    def enter_selection_mode(self):
        self.selection_mode = True
        self.selected_files.clear()
        self.update_search_row_icons()
        # Show checkboxes and delete icons
        for i, (file_rect, delete_icon, checkbox) in enumerate(self.file_rects):
            checkbox.setVisible(True)
            checkbox.setChecked(False)
        self.update()

    def exit_selection_mode(self):
        self.selection_mode = False
        self.selected_files.clear()
        self.update_search_row_icons()
        for i, (file_rect, delete_icon, checkbox) in enumerate(self.file_rects):
            checkbox.setVisible(False)
            checkbox.setChecked(False)
        self.update()

    def select_all_files(self):
        for i, (file_rect, delete_icon, checkbox) in enumerate(self.file_rects):
            checkbox.setChecked(True)
        self.update()

    def delete_selected_files(self):
        file_names = get_all_files()
        for idx, (file_rect, delete_icon, checkbox) in enumerate(self.file_rects):
            if checkbox.isChecked():
                filename = file_names[idx]
                self.delete_file(filename)
        self.exit_selection_mode()

    def toggle_select_all_files(self):
        file_count = len(self.file_rects)
        all_selected = all(cb.isChecked() for _, _, cb in self.file_rects) and file_count > 0
        if all_selected:
            for _, _, cb in self.file_rects:
                cb.setChecked(False)
        else:
            for _, _, cb in self.file_rects:
                cb.setChecked(True)
        self.update()

    def open_add_file_dialog(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add a Document", "", "Documents (*.pdf *.docx *.txt *.csv)")
        if file_path:
            print(f"Selected file: {file_path}")
            self.generate_questions_for_file(file_path)

    def generate_questions_for_file(self, file_path):
        script_path = f"{get_project_root()}/src/backend/dashboard/generate_questions.py"
        result = subprocess.run(
            [sys.executable, script_path, file_path],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Error:", result.stderr)
        input_filename = os.path.basename(file_path)
        base, _ = os.path.splitext(input_filename)
        json_filename = f"{base}.json"
        add_file_to_db(json_filename)
        self.refresh_file_list()

    def on_search_text_changed(self, text):
        self.refresh_file_list()

    def refresh_file_list(self):
        if not hasattr(self, 'files_layout'):
            self.files_layout = QVBoxLayout()
        self.file_rects.clear()
        self.file_checkboxes.clear()
        # Remove all widgets from the file list layout
        while self.file_list_layout.count():
            item = self.file_list_layout.takeAt(0)
            if not item:
                continue;
            widget = item.widget()
            if widget:
                widget.deleteLater()
        file_names = get_all_files()
        # Filter files by search query
        search_query = self.search_box.text().strip().lower() if hasattr(self, 'search_box') else ''
        if search_query:
            file_names = [fn for fn in file_names if search_query in fn.lower()]
        for filename in file_names:
            file_rect = QFrame()
            file_rect.setMinimumHeight(56)
            file_rect.setStyleSheet('background-color: #12284D; border-radius: 12px; border: 0.5px solid #fff;')
            file_row = QHBoxLayout(file_rect)
            file_row.setContentsMargins(0, 0, 10, 0)
            file_row.setSpacing(0)
            checkbox = QCheckBox()
            checkbox.setStyleSheet('QCheckBox { margin-left: 12px; margin-right: 8px; } QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; background: #22304a; border: 1.5px solid #b0b0b0; } QCheckBox::indicator:checked { background: #4fd1ff; border: 1.5px solid #4fd1ff; }')
            checkbox.setVisible(self.selection_mode)
            file_row.addWidget(checkbox)
            self.file_checkboxes.append(checkbox)
            file_label = QLabel(filename)
            file_label.setStyleSheet('color: #fff; font-size: 16px; font-weight: bold; padding-left: 18px; background: transparent; border: none;')
            file_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            file_row.addWidget(file_label)
            file_row.addStretch(1)
            edit_icon = QSvgWidget(icons.get_path('edit.svg'))
            edit_icon.setFixedSize(24, 24)
            edit_icon.setStyleSheet('background: transparent; border: none; margin-right: 18px;')
            file_row.addWidget(edit_icon)
            file_row.addSpacing(10)
            delete_icon = QSvgWidget(icons.get_path('delete.svg'))
            delete_icon.setFixedSize(24, 24)
            delete_icon.setStyleSheet('background: transparent; border: none;')
            delete_icon.setVisible(True)
            delete_icon.mousePressEvent = lambda e, fn=filename: self.delete_file(fn)
            file_row.addWidget(delete_icon)
            self.file_rects.append((file_rect, delete_icon, checkbox))
            self.file_list_layout.addWidget(file_rect)
        self.files_layout.addLayout(self.file_list_layout)

    def delete_file(self, filename):
        delete_file_from_db(filename)
        file_path = os.path.join('jsons', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        self.refresh_file_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DashboardScreen()
    window.show()
    sys.exit(app.exec()) 
