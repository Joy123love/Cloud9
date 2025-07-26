import sys
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QStackedWidget, QLineEdit, QCheckBox, QFileDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QPixmap, QPainter, QColor, QImage, QLinearGradient, QBrush, QPen, QPainterPath
from PyQt6.QtCore import QRectF
from PyQt6.QtSvgWidgets import QSvgWidget
import re
import os
from functools import partial
import subprocess
from backend.dashboard.notepad_db import init_db, add_file_to_db, get_all_files, delete_file_from_db
from assets import icons
import routes;
from coding.details import ChallengeDetails

from dashboard.banner import GreetingBanner
from dashboard.constants import GAMES
from dashboard.mini_games_cards import PopularCards, GamesCards
from dashboard.sidebar import DashboardRightPanel, DashboardSidebar
from dashboard.search import DashboardSearchbar
from dashboard.files import DashboardFiles
from dashboard.challenges import ChallengesCards
from theming.theme import theme
from utils import get_project_root

class DashboardScreen(QWidget):
    def __init__(self, username="Guest", user_id="Guest"):
        super().__init__()
        self.setAutoFillBackground(True);
        self.setStyleSheet(f'background-color: {theme.background_alternative.name()}; border-radius : 25px')  # Darker background for main window
        self.selected_sidebar_index = 0  # 0: Home, 1: File Plus, 2: Settings
        self.sidebar_icons = []
        self.selection_mode = False
        self.username = username;
        self.user_id = user_id;

        init_db()
        self.files_layout = QVBoxLayout()  # Ensure this is always defined
        self.init_ui()
        self.files.refresh_file_list()  # Always show files from the database on startup

    def init_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.sidebar = DashboardSidebar(self.sidebar_icon_clicked)

        # Main content area (now inside a vertical scroll area)
        # QStackedWidget for main content area
        self.content_stack = QStackedWidget()
        # Home page (current dashboard)
        home_inner = QFrame()
        home_inner.setStyleSheet('background: transparent; border-radius: 20px;')
        home_layout = QVBoxLayout(home_inner)
        # Add greeting and popular games as before
        self.greetings_banner = GreetingBanner(self.username)
        home_layout.addWidget(self.greetings_banner)
        popular_label = QLabel('Popular Games')
        popular_label.setStyleSheet(f'color: {theme.text.name()}; font-size: 15px; font-weight: bold; margin-top: 24px; margin-bottom: 0px;')
        home_layout.addWidget(popular_label)
        self.popular_cards = PopularCards(GAMES)
        home_layout.addWidget(self.popular_cards)
        # Add 'Games' section (grid list)
        games_label = QLabel('Challenges')
        games_label.setStyleSheet(f'color: {theme.text.name()}; font-size: 15px; font-weight: bold; margin-top: 24px; margin-bottom: 8px;')
        home_layout.addWidget(games_label)
        self.games_cards = ChallengesCards();
        home_layout.addWidget(self.games_cards)
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
        files_label.setStyleSheet(f'color: {theme.text.name()}; font-size: 22px; font-weight: bold; margin-top: 32px;')
        files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        files_layout.addWidget(files_label)

        # Placeholder file list
        self.files = DashboardFiles()
        self.search_bar = DashboardSearchbar(self.files.on_search_text_changed);

        files_layout.addWidget(self.search_bar)
        files_layout.addWidget(self.files)
        
        self.update_search_row_icons()
        files_layout.addStretch()
        # Settings page (placeholder)
        settings_frame = QFrame()
        settings_frame.setStyleSheet('background: transparent; border-radius: 20px;')
        settings_layout = QVBoxLayout(settings_frame)
        settings_label = QLabel('Settings Section')
        settings_label.setStyleSheet(f'color: {theme.text.name()}; font-size: 22px; font-weight: bold; margin-top: 32px;')
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
        self.right_panel = DashboardRightPanel(self.username, self.user_id);

        # Add widgets to main layout in correct order
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, stretch=2)
        main_layout.addWidget(self.right_panel)

        self.setLayout(main_layout)

    def update_search_row_icons(self):
        def get_icon(path : str, func) -> QSvgWidget:
            icon = QSvgWidget(path)
            icon.setFixedSize(28, 28)
            icon.setStyleSheet('background: transparent; margin-right: 10px;')
            icon.mousePressEvent = func
            return icon

        # Clear the search row
        while self.search_bar.search_row.count():
            item = self.search_bar.search_row.takeAt(0)
            if not item:
                continue
            widget = item.widget()
            # Only delete icons, not the persistent search box
            if widget and widget is not self.search_bar.search_box:
                widget.deleteLater()
        self.search_bar.search_row.addWidget(self.search_bar.search_box)
        self.search_bar.search_row.addStretch(1)
        file_count = len(self.files.file_rects)  # <-- Ensure file_count is defined before use
        if not self.selection_mode:
            # Normal mode: select and add-file icons
            if file_count > 0:
                select_icon = get_icon(icons.get_path("select.svg"), lambda e: self.enter_selection_mode());
                self.search_bar.search_row.addWidget(select_icon)
            add_file_icon = get_icon(icons.get_path("add-file.svg"), lambda e: self.files.open_add_file_dialog());
            self.search_bar.search_row.addWidget(add_file_icon)
        else:
            x_icon = get_icon(icons.get_path("x.svg"), lambda e: self.exit_selection_mode());
            self.search_bar.search_row.addWidget(x_icon)
            all_selected = all(file.checkbox.isChecked() for file in self.files.file_rects) and file_count > 0
            select_all_icon = get_icon(icons.get_path('deselect-all.svg' if all_selected else 'select-all.svg'), lambda e: self.toggle_select_all_files());
            self.search_bar.search_row.addWidget(select_all_icon)
            delete_icon = get_icon(icons.get_path('delete.svg'), lambda e: self.delete_selected_files())
            self.search_bar.search_row.addWidget(delete_icon)
        self.search_bar.search_row.update()

    def sidebar_icon_clicked(self, idx):
        self.content_stack.setCurrentIndex(idx)

    def enter_selection_mode(self):
        self.selection_mode = True
        self.update_search_row_icons()
        self.files.enter_selection_mode();
        self.update()

    def exit_selection_mode(self):
        self.selection_mode = False
        self.update_search_row_icons()
        self.files.exit_selection_mode();
        self.update()

    def select_all_files(self):
        self.files.select_all_files()
        self.update()

    def delete_selected_files(self):
        self.files.delete_selected_files()
        self.exit_selection_mode()

    def toggle_select_all_files(self):
        self.files.toggle_select_all_files();
        self.update()

    def open_add_file_dialog(self, event=None):
        file_path, _ = QFileDialog.getOpenFileName(self, "Add a Document", "", "Documents (*.pdf *.docx *.txt *.csv)")
        if file_path:
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
        self.files.refresh_file_list()
