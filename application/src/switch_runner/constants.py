import random
import os
import time
import math

def get_assets_path(name : str) -> str:
    return f"./assets/games/switch_runner/{name}";
# Fixed window size
WIDTH, HEIGHT = 1280, 720
PLATFORM_Y_TOP = HEIGHT // 6
PLATFORM_Y_BOTTOM = 5 * HEIGHT // 6
PLATFORM_THICKNESS = 12
BALL_RADIUS = 36
BALL_START_X = 220
BALL_SPEED = 7  # Increased horizontal speed
PICKABLE_ANIM_SPEED = 6  # frames per animation step
HURT_ANIM_SPEED = 6
DEATH_ANIM_SPEED = 6
OBSTACLE_WIDTH = 56
OBSTACLE_HEIGHT = 84

CHARACTER_WIDTH = 0
CHARACTER_HEIGHT = 0

LIVES = 3
FPS = 60
GLIDE_FRAMES = 20  # Number of frames for glide animation

ANCHOR_X = int(WIDTH * 0.4)  # Ball stays at 40% of the screen
SPAWN_INTERVAL_SLOW = 90
SPAWN_INTERVAL_FAST = 45
MATH_INTERVALS = [15, 17, 21, 29, 33, 46, 54, 67]
POWERUP_RADIUS = 28
POWERUP_COLOR = (255, 215, 0)
POWERUP_TYPE_INVINCIBLE = 'invincible'
POWERUP_TYPE_HEART = 'heart'
PICKABLE_SPAWN_INTERVAL = 90 * 3  # Less frequent than obstacles

PICKABLE_RADIUS = 24
PICKABLE_COLOR = (80, 220, 120)
CHARACTER_SHEET_PATH = get_assets_path("characters/animations/dude/Dude_Monster_Run_6.png")
CHARACTER_FRAMES = 6
HURT_SHEET_PATH = get_assets_path("characters/animations/dude/Dude_Monster_Hurt_4.png")
HURT_FRAMES = 4
DEATH_SHEET_PATH = get_assets_path("characters/animations/dude/Dude_Monster_Death_8.png")
DEATH_FRAMES = 8
XP_COIN_PATH = get_assets_path("objects/xp_coin")
XP_COIN_FRAMES = 6
SPIKES_PATH = get_assets_path("objects/Spikes.png")
SPIKES_FRAMES = 4
CHARACTER_ANIM_SPEED = 4  # Lower is faster

PLAYER_IMAGE_PATH = get_assets_path("characters/select/Dude_Monster.png")
ENTITY_IMAGE_PATH = get_assets_path("characters/entity/download (1).jpeg")
BUBBLE_PATH = get_assets_path("objects/Bubble.png")
LIFE_PATH = get_assets_path("objects/Life.png")
MATH_LAUGH_DURATION = 1.2

STARTING_DIALOGUE = [
    ("entity", "I have kidnapped Ursula and I will not bring her back."),
    ("player", "What, who are you?"),
    ("entity", "I am, the Entity."),
    ("player", "Give back Ursula right now."),
    ("entity", "I will if you play a little game with me. Answer this question, Will you play the game or not?")
]

# Parallax background settings
BG_ROOT = get_assets_path("backgrounds/")
CLOUD_FOLDERS = [f'Clouds{i}/' for i in range(1, 9)]
BG_FOLDER = random.choice(CLOUD_FOLDERS)
BG_PATH = os.path.join(BG_ROOT, BG_FOLDER)
BG_LAYERS = [
    {'file': '1.png', 'speed': 0.2},
    {'file': '2.png', 'speed': 0.4},
    {'file': '3.png', 'speed': 0.7},
    {'file': '4.png', 'speed': 1.0},
]
