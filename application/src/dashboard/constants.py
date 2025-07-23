import routes
from coding.details import ChallengeDetails
from authentication.session import USER_ID


GAMES = [
        {
            "name" : "Create Coding Challenge", 
            "func" : lambda e: routes.open_coding_create(ChallengeDetails(name="New Challenge", user_id=USER_ID, description="", starting="", statements={}, checks=[]))
        },
        {
            "name" : "Switch Runner", 
            "func" : lambda e: routes.open_switch_runner()
        }
];
