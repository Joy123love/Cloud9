from dataclasses import dataclass
from PyQt6.QtGui import QIcon

from utils import get_project_root

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
    cancel : QIcon
    export_notes : QIcon
    facebook : QIcon
    google : QIcon
    linkedin : QIcon


def get_default_icons() -> Icons:
    def get_path(name : str):
        return f"{get_project_root()}/src/assets/icons/" + name;

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
        cancel=QIcon(get_path("cancel.svg")),
        export_notes=QIcon(get_path("export_notes.svg")),
        facebook=QIcon(get_path("facebook.png")),
        google=QIcon(get_path("google.png")),
        linkedin=QIcon(get_path("linkedin.png")),
    );

icons : Icons = get_default_icons();
