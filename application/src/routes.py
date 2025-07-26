from typing import Callable, Optional

from PyQt6.QtGui import QPalette
from coding.details import ChallengeDetails

# Helpers
set_background_style: Optional[Callable[[Optional[str]], None]] = None;
reset_palette: Optional[Callable[[], None]] = None;
set_colour_role: Optional[Callable[[QPalette.ColorRole], None]] = None;
set_user: Optional[Callable[[str, str], None]] = None;
get_user: Optional[Callable[[], tuple[str, str]]] = None;

# Routes
open_dashboard : Optional[Callable[[], None]] = None;
open_signup : Optional[Callable[[], None]] = None;
open_login : Optional[Callable[[], None]] = None;
open_coding_create : Optional[Callable[[ChallengeDetails], None]] = None;
open_coding_play : Optional[Callable[[ChallengeDetails], None]] = None;
open_switch_runner : Optional[Callable[[], None]] = None;
open_flappy_learn : Optional[Callable[[], None]] = None;
