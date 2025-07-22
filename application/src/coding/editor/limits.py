from enum import Enum
import keyword
from typing import Optional

def get_default_words() -> dict[str, int]:
    allowed = {};
    for word in keyword.kwlist:
        allowed.update({word: 10000});
    return allowed

class LimitFailure(Enum):
    SURPASSED_MAXIMUM = 0

class Limits:
    def __init__(self, allowed : dict[str, int] = get_default_words()):
        self.keywords = allowed;

    def is_valid(self, text : str) -> Optional[LimitFailure]:
        used = {};
        for word in text.split():
            maximum = self.keywords.get(word);
            if maximum is None:
                continue;
            amt = used.get(word);

            if amt is None:
                used.update({word : 1});
            elif amt > maximum:
                return LimitFailure.SURPASSED_MAXIMUM;
            else:
                amt =  + 1;
                used.update({word : amt});

        return None
