import routes
from coding.details import ChallengeDetails

GAMES = [
        {
            "name" : "Create Coding Challenge", 
            "func" : lambda e: routes.open_coding_create(ChallengeDetails(name="New Challenge", user_id="",description="", starting="", statements={}, checks=[])),
            "image" : "Code.png",
        },
        {
            "name" : "Switch Runner", 
            "func" : lambda e: routes.open_switch_runner(),
            "image" : "Runner.png",
        },
        {
            "name" : "Flappy Learn", 
            "func" : lambda e: routes.open_flappy_learn(),
            "image" : "basketbird.png",  # You can replace this with a custom image later
        },
];
