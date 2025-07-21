from dataclasses import dataclass, field
from PyQt6.QtGui import QColor, QFont, QPalette

@dataclass
class Theme:
    background : QColor
    background_alternative : QColor
    primary_dark : QColor
    primary : QColor
    secondary : QColor
    tertiary : QColor
    danger : QColor 
    text : QColor

def get_default_theme() -> Theme:
    return Theme(
        background=QColor("#11111b"),
        background_alternative=QColor("#1e1e2e"),
        primary_dark=QColor("#2c1f4b"),
        primary=QColor("#cba6f7"),
        secondary=QColor("#a6e3a1"),
        tertiary=QColor("#f9e2af"),
        danger=QColor("#f38ba8"),
        text=QColor("#efe9fc")
    );

theme : Theme = get_default_theme();

def get_palette_from_theme(theme : Theme) -> QPalette:
    palette = QPalette();

    palette.setColor(QPalette.ColorRole.Window, theme.background);
    palette.setColor(QPalette.ColorRole.Text, theme.text);
    palette.setColor(QPalette.ColorRole.AlternateBase, theme.background_alternative);
    palette.setColor(QPalette.ColorRole.PlaceholderText, theme.text.darker(2));
    palette.setColor(QPalette.ColorRole.Base, theme.background);
    return palette;

def get_current_theme() -> Theme:
    return theme;
