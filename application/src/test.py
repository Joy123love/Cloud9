from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


class ExtraMainScreen(QMainWindow):
    def __init__(self, widget : QWidget):
        super().__init__()

        self.setCentralWidget(widget);


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    from theming.theme import get_palette_from_theme, theme
    from coding.create.screen import CreateCodingGameScreen
    from coding.play.screen import PlayCodingGameScreen
    from quizzes.guess.screen import GuessQuizScreen
    from quizzes.create.screen import CreateQuizScreen
    from authentication.login_window import LoginWindow
    from authentication.signup_window import SignUpWindow
    from switch_runner.screen import SwitchRunnerScreen
    from dashboard.screen import DashboardScreen
    # TODO Routes - For now comment in the appropriate screens;
    # window = CreateCodingGameScreen();
    # window = PlayCodingGameScreen();
    # window = GuessQuizScreen();
    # window = CreateQuizScreen()
    # window = SwitchRunnerScreen();

    # window = ExtraMainScreen(LoginWindow());
    window = ExtraMainScreen(DashboardScreen());
    # window = ExtraMainScreen(SignUpWindow());

    window.setPalette(get_palette_from_theme(theme));
    window.show()
    sys.exit(app.exec())
