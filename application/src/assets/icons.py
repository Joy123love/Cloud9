from dataclasses import dataclass
from PyQt6.QtGui import QIcon

@dataclass
class Icons:
    calculate : QIcon
    check : QIcon
    code : QIcon
    experiment : QIcon
    fire : QIcon
    language : QIcon
    orbit : QIcon
    stories : QIcon
    delete : QIcon
    add : QIcon


def get_default_icons() -> Icons:
    def get_path(name : str):
        return "./assets/icons/" + name;

    return Icons(
        calculate=QIcon(get_path("calculate.svg")),
        check=QIcon(get_path("check.svg")),
        code=QIcon(get_path("code.svg")),
        experiment=QIcon(get_path("experiment.svg")),
        fire=QIcon(get_path("fire.svg")),
        language=QIcon(get_path("language.svg")),
        orbit=QIcon(get_path("orbit.svg")),
        stories=QIcon(get_path("stories.svg")),
        delete=QIcon(get_path("delete.svg")),
        add=QIcon(get_path("add.svg")),
    );

icons : Icons = get_default_icons();
