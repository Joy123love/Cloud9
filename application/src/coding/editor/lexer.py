from PyQt6.Qsci import (QsciScintilla, QsciLexerPython);
import sys

from theming.theme import Theme;
from theming.font import Font;

class CustomLexer(QsciLexerPython):
    def __init__(self, theme : Theme, font : Font, *args, **kwargs):
        super().__init__(*args, **kwargs);

        self.setDefaultFont(font.default);
        self.setDefaultColor(theme.text);
        self.setColor(theme.background_alternative, self.Comment);
        self.setColor(theme.primary, self.Keyword);
        self.setColor(theme.text, self.ClassName);
        self.setPaper(theme.background);
