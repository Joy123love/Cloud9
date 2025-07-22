from typing import Callable, Optional

# Helpers
set_background_style : Optional[Callable[[str|None], None]] = None;

# Routes
open_dashboard : Optional[Callable[[], None]] = None;
open_signup : Optional[Callable[[], None]] = None;
open_login : Optional[Callable[[], None]] = None;
open_coding_create : Optional[Callable[[], None]] = None;
open_coding_play : Optional[Callable[[], None]] = None;
