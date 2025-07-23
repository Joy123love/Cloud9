from typing import Callable, Optional
from coding.details import ChallengeDetails

# Helpers
set_background_style: Optional[Callable[[Optional[str]], None]] = None;

# Routes
open_dashboard : Optional[Callable[[str], None]] = None;
open_signup : Optional[Callable[[], None]] = None;
open_login : Optional[Callable[[], None]] = None;
open_coding_create : Optional[Callable[[ChallengeDetails], None]] = None;
open_coding_play : Optional[Callable[[ChallengeDetails], None]] = None;
open_switch_runner : Optional[Callable[[], None]] = None;
