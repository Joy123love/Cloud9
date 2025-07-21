import sys
from .limits import Limits;
from .lexer import CustomLexer; 
from typing import Any
from theming.theme import theme;
from theming.font import font;
from PyQt6.Qsci import (QsciScintilla);
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFontMetrics,  QKeySequence, QAction

class CodeEditor(QsciScintilla):
    def __init__(self, text : str = "",*args, **kwargs):
        super().__init__(*args, **kwargs);
        self.setLexer(CustomLexer(theme, font));
        self.setPaper(theme.background);
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll);
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionFillupsEnabled(True)
        self.setTabWidth(4)
        self.setMarginLineNumbers(1, True)
        self.setAutoIndent(True)
        self.setMarginWidth(5, theme.text.name())
        self.setText(text);

        left_margin_index = 0
        left_margin_width = 7
        font_metrics = QFontMetrics(self.font())
        left_margin_width_pixels = font_metrics.horizontalAdvance(" ") * left_margin_width
        self.SendScintilla(self.SCI_SETMARGINLEFT, left_margin_index, left_margin_width_pixels)
        
        self.setMarginsForegroundColor(QColor(theme.text))
        self.setMarginsBackgroundColor(QColor(theme.background))
        self.setFoldMarginColors(
            QColor(theme.background), QColor(theme.background)
        )
        self.setCaretLineVisible(True);
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
        self.setMarginSensitivity(2, True)
        self.setBraceMatching(QsciScintilla.BraceMatch.StrictBraceMatch)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(theme.background)
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)
        self.setAutoCompletionThreshold(1)
        self.setBackspaceUnindents(True)
        self.setIndentationGuides(True)
        self.setReadOnly(False)
        self.context_menu = QMenu(self)
        self.context_menu.addAction("Run").triggered.connect(lambda : self.run())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def run(self, limits : Limits = Limits()) -> dict[str, Any]:
        validity = limits.is_valid(self.text());

        if validity is None:
            locals = {};
            exec(self.text(), locals);
            return locals
        else:
            print("Invalid Code");
            locals = {};
            exec(self.text(), locals);
            return locals


    def show_context_menu(self, point):
        self.context_menu.popup(self.mapToGlobal(point))
