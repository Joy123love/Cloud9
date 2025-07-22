from dataclasses import dataclass

@dataclass
class ChallengeDetails:
    name : str
    user_id : int
    description : str
    starting : str
    statements : dict[str, int]
    checks : list[str]
