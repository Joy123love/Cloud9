# Custom BannerFrame for scaled background image and overlay
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QPainter, QPainterPath, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from theming.theme import theme
from utils import get_project_root


class BannerFrame(QFrame):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = QPixmap(self.image_path)
        self.setMinimumHeight(120)
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
        # overlay_color = QColor(20, 30, 50, int(255 * 0.45))  # 45% opacity dark overlay
        overlay_color = theme.background_alternative
        overlay_color.setAlpha(int(255 * 0.45));
        painter.setBrush(overlay_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 16, 16)
        super().paintEvent(event)


class GreetingBanner(BannerFrame):
    def __init__(self, username, *args, **kwargs):
        super().__init__(f"{get_project_root()}/src/assets/images/banner2.jpeg", *args, **kwargs);
        greeting_layout = QVBoxLayout(self)
        greeting_layout.setContentsMargins(32, 16, 32, 16)
        greeting_label = QLabel(f'Hello, {username}')
        greeting_label.setStyleSheet('color: #ffffff; font-size: 24px; font-weight: bold; background: transparent;')
        greeting_sub = QLabel('Welcome back to our platform')
        greeting_sub.setStyleSheet('color: #b0c4de; font-size: 14px; background: transparent;')
        greeting_layout.addWidget(greeting_label)
        greeting_layout.addWidget(greeting_sub)
