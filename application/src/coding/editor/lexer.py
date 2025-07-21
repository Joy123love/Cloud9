from PyQt6.Qsci import (QsciScintilla, QsciLexerPython);
import sys

from theming.theme import Theme;
from theming.font import Font;

class CustomLexer(QsciLexerPython):
    def __init__(self, theme : Theme, font : Font, *args, **kwargs):
        super().__init__(*args, **kwargs);

        self.setDefaultFont(font.default);
        self.setDefaultColor(theme.text);
        self.setColor(theme.text.darker(2), self.Comment);
        self.setColor(theme.text.darker(2), self.CommentBlock);
        self.setColor(theme.primary, self.Keyword);
        self.setColor(theme.text, self.ClassName);
        self.setColor(theme.text, self.SingleQuotedString);
        self.setColor(theme.text, self.SingleQuotedFString);
        self.setColor(theme.text, self.DoubleQuotedString);
        self.setColor(theme.text, self.DoubleQuotedFString);
        self.setColor(theme.text, self.UnclosedString);
        self.setColor(theme.text, self.FunctionMethodName)
        self.setColor(theme.secondary, self.Number);

        self.setPaper(theme.background);
