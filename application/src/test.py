from PyQt6.QtWidgets import QApplication
from coding.create.screen import CreateCodingGameScreen
from coding.play.screen import PlayCodingGameScreen
from quizzes.guess.screen import GuessQuizScreen
from quizzes.create.screen import CreateQuizScreen
from switch_runner.screen import SwitchRunnerScreen
from theming.theme import get_palette_from_theme, theme

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    # TODO Routes - For now comment in the appropriate screens;
    # window = CreateCodingGameScreen();
    window = PlayCodingGameScreen();
    # window = GuessQuizScreen();
    # window = CreateQuizScreen()
    # window = SwitchRunnerScreen();

    window.setPalette(get_palette_from_theme(theme));
    window.show()
    sys.exit(app.exec())
