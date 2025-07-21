from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from quizzes.details import QuestionDetails, QuizDetails
from quizzes.create.options import CreateQuizOptions
from quizzes.create.question import CreateQuestion
from quizzes.create.sidebar import CreateSidebar


class CreateQuizScreen(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs);

        details = QuizDetails("Test Project", "Taida", "Finish The App", [QuestionDetails("How are you doing?", ["Good", "Bad", "Horrible", "Fantastic"], [0, 2])])
        editor_layout = QVBoxLayout();
        self.question = CreateQuestion(details.questions[0].question);
        editor_layout.addWidget(self.question);
        editor_layout.addSpacing(250); 
        self.answers = CreateQuizOptions(details.questions[0].answers);
        editor_layout.addWidget(self.answers);

        right = QWidget();
        right.setLayout(editor_layout);

        self.setBackgroundRole(QPalette.ColorRole.AlternateBase);
        self.setAutoFillBackground(True);

        self.side = CreateSidebar(details);

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.side);
        self.setCentralWidget(right)
