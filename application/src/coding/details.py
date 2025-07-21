from dataclasses import dataclass

@dataclass
class ChallengeDetails:
    name : str
    username : str
    description : str
    starting : str
    statements : dict[str, int]
    checks : list[str]
