import pygame
import sys
import os
import math
import random
import time
import requests

# Settings
WIDTH, HEIGHT = 800, 600
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, '../assets/games/flappy_learn')  # New asset folder

# Define border and divider thickness for drawing
BORDER_THICKNESS = 60
DIVIDER_THICKNESS = 8

# Define ring size constants before hoop setup
RING_WIDTH = 110
RING_HEIGHT = 75

# Initialize Pygame
pygame.init()

# --- Add background music ---
MUSIC_PATH = os.path.join(ASSETS_DIR, 'The Theme from a Summer Place - Percy Faith.mp3')
try:
    pygame.mixer.init()
    pygame.mixer.music.load(MUSIC_PATH)
    pygame.mixer.music.play(-1)  # Loop indefinitely
except Exception as e:
    print(f"Could not play music: {e}")
# --- End music addition ---

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Learn - Parallax Demo (Fresh)")
clock = pygame.time.Clock()

# List of background folders
BG_FOLDERS = [
    os.path.join(ASSETS_DIR, f'clouds{i}') for i in range(1, 5)
]
current_bg_index = 0

# Function to load layers from a folder
def load_layers(folder):
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith('.png')])
    loaded_layers = []
    for filename in files:
        path = os.path.join(folder, filename)
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        loaded_layers.append(img)
    return loaded_layers

# Initial background layers
FOLDER = BG_FOLDERS[current_bg_index]
layers = load_layers(FOLDER)
if len(layers) > 1:
    speeds = [0.01 + 0.06 * i/(len(layers)-1) for i in range(len(layers))]
else:
    speeds = [0.05]
offsets = [0.0 for _ in layers]

# Fade transition variables
fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
fade_surface.fill((0, 0, 0, 255))  # Full black, alpha will be set dynamically
fade_alpha = 0
fade_direction = 0  # 0: no fade, 1: fade out, -1: fade in
fade_speed = 1.2  # Slightly faster fade (was 0.67)

# Timer for background switching
last_switch_time = time.time()
switch_interval = 15  # seconds

# Load score board images
SCORE_ASSETS = ASSETS_DIR  # All images in the main flappy_learn asset folder

# Load main ball image
main_ball_img = pygame.image.load(os.path.join(SCORE_ASSETS, 'main ball.png')).convert_alpha()
BALL_HEIGHT = 44  # Smaller ball
BALL_WIDTH = int(main_ball_img.get_width() * BALL_HEIGHT / main_ball_img.get_height())
main_ball_img = pygame.transform.scale(main_ball_img, (BALL_WIDTH, BALL_HEIGHT))
# Ball position: centered vertically, towards left
ball_x = 60  # 60px from left edge
ball_y = (HEIGHT - BALL_HEIGHT) // 2
ball_vel = 0

# Load wing images
wing1_img = pygame.image.load(os.path.join(SCORE_ASSETS, 'wing1.png')).convert_alpha()
wing2_img = pygame.image.load(os.path.join(SCORE_ASSETS, 'wing2.png')).convert_alpha()
# Scale wings to fit ball height
WING_HEIGHT = int(BALL_HEIGHT * 1.1)  # larger wings relative to ball
WING_WIDTH = int(wing1_img.get_width() * WING_HEIGHT / wing1_img.get_height())
wing1_img = pygame.transform.scale(wing1_img, (WING_WIDTH, int(WING_HEIGHT)))
wing2_img = pygame.transform.scale(wing2_img, (WING_WIDTH, int(WING_HEIGHT)))

# Wing animation variables
wing_angle = 0  # Current angle of the wings
wing_swipe = False  # Is the swipe animation active?
wing_swipe_progress = 0  # Progress of the swipe (frames)
WING_SWIPE_MAX = 40  # Maximum downward angle in degrees
WING_SWIPE_SPEED = 6  # Degrees per frame for swipe
WING_SWIPE_RETURN_SPEED = 4  # Degrees per frame for return

# Ball rolling (spinning) effect variables
ball_angle = 0.0
SPIN_STEP = -8  # degrees per frame (slower, counterclockwise spin)

GRAVITY = 0.7
JUMP_STRENGTH = -10
BOUNCE_DAMPING = 0.35  # Even stronger damping
BOUNCE_MIN = 3.5  # Slightly higher threshold to stop bouncing
BOUNCE_START = -10  # More dramatic initial bounce
BOUNCE_VX_START = 8  # More dramatic initial horizontal movement
BOUNCE_GRAVITY = 1.0  # Stronger gravity

# Game over and deceleration variables
ball_vx = 0
BALL_ROLL_DECEL = 0.18
BG_DECEL = 0.005
SCORE_DECEL = 2
bg_speed_factor = 1.0
score_speed_factor = 1.0
game_over = False

# Bouncing and rolling state
ball_bouncing = False
bounce_vel = 0
bounce_vx = 0

# Add background pause timer
background_paused_until = 0
BACKGROUND_PAUSE_DURATION = 0.3  # seconds

# Add background pause flag
background_paused = False

# Define collision rectangles for green-highlighted areas (assuming ring image is 292x293, scale if needed)
COLLISION_RECTS = [
    pygame.Rect(0, 0, 40, 40),  # left attachment
    pygame.Rect(252, 0, 40, 40) # right attachment
]
collision_mode = False

# Coin system setup (replacing hoops)
COIN_RADIUS = 24
COIN_ANIM_SPEED = 6  # frames per animation step
COIN_SPAWN_INTERVAL = 90 * 3  # Less frequent than obstacles
XP_COIN_FRAMES = 6  # Number of coin animation frames

# Load coin images (user will copy XP coin images to assets/games/flappy_learn/coins/)
XP_COIN_PATH = os.path.join(ASSETS_DIR, 'coins')
xp_coin_images = []
try:
    for i in range(1, XP_COIN_FRAMES + 1):
        img_path = os.path.join(XP_COIN_PATH, f'Coin_{i:02d}.png')
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (COIN_RADIUS * 2, COIN_RADIUS * 2))
        xp_coin_images.append(img)
except Exception as e:
    print(f"Could not load coin images: {e}")
    # Create fallback coin images
    xp_coin_images = []
    for i in range(XP_COIN_FRAMES):
        coin_surface = pygame.Surface((COIN_RADIUS * 2, COIN_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(coin_surface, (255, 215, 0), (COIN_RADIUS, COIN_RADIUS), COIN_RADIUS)
        pygame.draw.circle(coin_surface, (255, 255, 0), (COIN_RADIUS, COIN_RADIUS), COIN_RADIUS - 4)
        xp_coin_images.append(coin_surface)

# Coins setup (replacing hoops)
coins = []  # List of (x, y, anim_index, anim_timer)
frame_count = 0

# Add state for DrBounce questions
answering_questions = False
questions = [
    ("What is 2 + 2?", "4"),
    ("What color is the sky on a clear day?", "blue"),
    ("What is the capital of France?", "paris")
]
school_questions = [
    ("What is the largest planet in our solar system?", "jupiter"),
    ("Who wrote 'Romeo and Juliet'?", "shakespeare"),
    ("What is the chemical symbol for water?", "h2o"),
    ("What is 9 x 7?", "63"),
    ("What year did World War II end?", "1945"),
    ("What is the square root of 81?", "9"),
    ("Who painted the Mona Lisa?", "da vinci"),
    ("What is the capital of Japan?", "tokyo"),
    ("What gas do plants breathe in?", "carbon dioxide"),
    ("What is the freezing point of water in Celsius?", "0")
]
current_question = 0
user_answer = ''
questions_passed = False
golden_hoops_left = 5
# Timed DrBounce quiz state
timed_quiz_active = False
timed_quiz_question = None
timed_quiz_answer = ''
timed_quiz_last_time = time.time()
timed_quiz_interval = 10
timed_quiz_feedback = None  # None, 'correct', or 'wrong'
timed_quiz_feedback_time = 0
# Waiting for user to press UP after DrBounce retry
waiting_for_replay_start = False
start_screen_stage = 0  # 0: intro, 1: press up to start, 2: game running
# Load DrBounce image
DRBOUNCE_IMG = pygame.image.load(os.path.join(SCORE_ASSETS, 'drbounce - intro.png')).convert_alpha()
DRBOUNCE_SIZE = 200
DRBOUNCE_IMG = pygame.transform.smoothscale(DRBOUNCE_IMG, (DRBOUNCE_SIZE, DRBOUNCE_SIZE))
# Load thinking dialog image
THINKING_IMG = pygame.image.load(os.path.join(SCORE_ASSETS, 'thinking.png')).convert_alpha()
THINKING_W, THINKING_H = 260, 100
THINKING_IMG = pygame.transform.smoothscale(THINKING_IMG, (THINKING_W, THINKING_H))
THINKING_IMG = pygame.transform.flip(THINKING_IMG, True, False)

UP_KEY_SIZE = (22, 22)
ESC_KEY_SIZE = (32, 22)
# Try to load a custom up button image, fallback to drawn version if not found
try:
    UP_KEY_IMG = pygame.image.load(os.path.join(SCORE_ASSETS, 'up_key.png')).convert_alpha()
    UP_KEY_IMG = pygame.transform.smoothscale(UP_KEY_IMG, UP_KEY_SIZE)
except Exception:
    UP_KEY_IMG = pygame.Surface(UP_KEY_SIZE, pygame.SRCALPHA)
    pygame.draw.rect(UP_KEY_IMG, (220, 220, 220), (0, 0, *UP_KEY_SIZE), border_radius=8)
    font_up = pygame.font.SysFont(None, 24, bold=True)
    up_text = font_up.render("↑", True, (40, 40, 40))
    UP_KEY_IMG.blit(up_text, up_text.get_rect(center=(UP_KEY_SIZE[0]//2, UP_KEY_SIZE[1]//2)))

ESC_KEY_IMG = pygame.Surface(ESC_KEY_SIZE, pygame.SRCALPHA)
pygame.draw.rect(ESC_KEY_IMG, (220, 220, 220), (0, 0, *ESC_KEY_SIZE), border_radius=8)
esc_text = pygame.font.SysFont(None, 24, bold=True).render("ESC", True, (40, 40, 40))
ESC_KEY_IMG.blit(esc_text, esc_text.get_rect(center=(ESC_KEY_SIZE[0]//2, ESC_KEY_SIZE[1]//2)))
# Pause button state
paused = False
PAUSE_BTN_SIZE = (64, 64)
PAUSE_BTN_RECT = pygame.Rect(WIDTH - PAUSE_BTN_SIZE[0] - 24, 24, *PAUSE_BTN_SIZE)
PAUSE_BTN_COLOR = (70, 130, 255)
PAUSE_BTN_ICON_COLOR = (255, 255, 255)
# Load golden hoop award image for top left border
GOLDEN_HOOP_IMG = pygame.image.load(os.path.join(SCORE_ASSETS, 'golden hoop award.png')).convert_alpha()
GOLDEN_HOOP_SIZE = 38
GOLDEN_HOOP_IMG = pygame.transform.smoothscale(GOLDEN_HOOP_IMG, (GOLDEN_HOOP_SIZE, GOLDEN_HOOP_SIZE))
background_moving = False
# Fix for NameError: prev_ball_center_y
prev_ball_center_y = ball_y + BALL_HEIGHT // 2

# Fix for NameError: score
score = 0

# Fix for NameError: now (used for background switching logic)
now = time.time()

def jump_ball():
    global ball_vel
    ball_vel = JUMP_STRENGTH

def spin_ball():
    pass

def restart_game():
    global game_over, ball_bouncing, background_moving, bg_speed_factor, score_speed_factor
    global ball_x, ball_y, ball_vel, ball_vx, ball_angle, wing_angle, wing_swipe, wing_swipe_progress
    global score, current_bg_index, FOLDER, layers, speeds, offsets, fade_alpha, fade_direction, last_switch_time
    global golden_hoops_left, coins, frame_count
    game_over = False
    ball_bouncing = False
    background_moving = False
    bg_speed_factor = 1.0
    score_speed_factor = 1.0
    ball_x = 60
    ball_y = (HEIGHT - BALL_HEIGHT) // 2
    ball_vel = 0
    ball_vx = 0
    ball_angle = 0.0
    wing_angle = 0
    wing_swipe = False
    wing_swipe_progress = 0
    score = 0
    golden_hoops_left = 5
    # Reset coins
    coins = []
    frame_count = 0
    # Reset background
    current_bg_index = 0
    FOLDER = BG_FOLDERS[current_bg_index]
    layers = load_layers(FOLDER)
    if len(layers) > 1:
        speeds = [0.01 + 0.06 * i/(len(layers)-1) for i in range(len(layers))]
    else:
        speeds = [0.05]
    offsets = [0.0 for _ in layers]
    fade_alpha = 0
    fade_direction = 0
    last_switch_time = now

# 1. Add this variable near other quiz state variables:
timed_quiz_user_input = ''

# 1. Add a feedback timer duration at the top (with other constants):
FEEDBACK_DISPLAY_TIME = 1.5  # seconds

while True:
    dt = clock.tick(60)  # ms since last frame
    # Precompute rotated wings for this frame
    rotated_wing1 = pygame.transform.rotate(wing1_img, wing_angle)
    rotated_wing2 = pygame.transform.rotate(wing2_img, wing_angle - 15)  # back wing starts 15 deg upward

    events = pygame.event.get()
    for event in events:
        # Always handle window close (QUIT) event first
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Handle intro screen UP button logic
        if start_screen_stage in (0, 1):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                if start_screen_stage == 0:
                    start_screen_stage = 1
                elif start_screen_stage == 1:
                    start_screen_stage = 2
                    background_moving = True
            continue
        # Block all gameplay input if quiz overlay is active
        if timed_quiz_active:
            # Only allow input for answering the question (e.g., alphanumeric, backspace, enter)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    timed_quiz_user_input = timed_quiz_user_input[:-1]
                elif event.key == pygame.K_RETURN:
                    # Check answer
                    if timed_quiz_user_input.strip().lower() == timed_quiz_answer.lower():
                        timed_quiz_feedback = 'correct'
                    else:
                        timed_quiz_feedback = 'wrong'
                        golden_hoops_left = max(0, golden_hoops_left - 1)
                        if golden_hoops_left == 0:
                            game_over = True
                    timed_quiz_active = False
                    timed_quiz_feedback_time = time.time()
                    # Don't resume background_moving yet
                    timed_quiz_user_input = ''
                elif event.unicode.isprintable():
                    timed_quiz_user_input += event.unicode
            continue  # Skip all other input/events while quiz is active
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over:
                    restart_game()
            elif event.key == pygame.K_TAB:
                if not game_over:
                    jump_ball()
                    wing_swipe = True
                    wing_swipe_progress = 0
                    spin_ball()
            elif not game_over and not ball_bouncing:
                if not background_moving:
                    background_moving = True
                if event.key == pygame.K_UP:
                    jump_ball()
                    wing_swipe = True
                    wing_swipe_progress = 0

    # --- Timed DrBounce Quiz Trigger ---
    if (
        not timed_quiz_active
        and not paused
        and not game_over
        and not (start_screen_stage in (0, 1))
        and background_moving
        and time.time() - timed_quiz_last_time > timed_quiz_interval
    ):
        timed_quiz_active = True
        timed_quiz_last_time = time.time()
        q, a = random.choice(school_questions)
        timed_quiz_question = q  # Only the question string
        timed_quiz_answer = a    # Only the answer string
        timed_quiz_user_input = ''
        timed_quiz_feedback = None
        timed_quiz_feedback_time = 0
        background_moving = False

    # --- Background transition trigger ---
    if (
        fade_direction == 0
        and not paused
        and not timed_quiz_active
        and not timed_quiz_feedback
        and not game_over
        and not waiting_for_replay_start
        and start_screen_stage == 2
        and (time.time() - last_switch_time > switch_interval)
    ):
        fade_direction = 1  # Start fade out

    if fade_direction == 1:  # Fading out
        fade_alpha += fade_speed
        if fade_alpha >= 255:
            fade_alpha = 255
            # Switch background
            current_bg_index = (current_bg_index + 1) % len(BG_FOLDERS)
            FOLDER = BG_FOLDERS[current_bg_index]
            layers = load_layers(FOLDER)
            if len(layers) > 1:
                speeds = [0.01 + 0.06 * i/(len(layers)-1) for i in range(len(layers))]
            else:
                speeds = [0.05]
            offsets = [0.0 for _ in layers]
            last_switch_time = now
            fade_direction = -1  # Start fade in
    elif fade_direction == -1:  # Fading in
        fade_alpha -= fade_speed
        if fade_alpha <= 0:
            fade_alpha = 0
            fade_direction = 0

    # Wing swipe animation logic
    if wing_swipe:
        if wing_swipe_progress < WING_SWIPE_MAX:
            wing_angle += WING_SWIPE_SPEED
            wing_swipe_progress += WING_SWIPE_SPEED
            if wing_angle > WING_SWIPE_MAX:
                wing_angle = WING_SWIPE_MAX
        else:
            wing_angle -= WING_SWIPE_RETURN_SPEED
            if wing_angle <= 0:
                wing_angle = 0
                wing_swipe = False

    # Ball physics update (after background_moving check)
    if background_moving and not game_over and not ball_bouncing:
        ball_vel += GRAVITY
        ball_y += int(ball_vel)
        # Prevent ball from leaving the screen vertically
        if ball_y < BORDER_THICKNESS:
            ball_y = BORDER_THICKNESS
            ball_vel = 0
        # Bounce on bottom black divider
        bottom_limit = HEIGHT - BORDER_THICKNESS - DIVIDER_THICKNESS - BALL_HEIGHT
        if ball_y > bottom_limit:
            ball_y = bottom_limit
            if ball_vel > 0:
                # Trigger bounce/roll sequence on bottom border
                ball_bouncing = True
                bounce_vel = BOUNCE_START
                bounce_vx = BOUNCE_VX_START
                background_moving = False
                bg_speed_factor = 0
                score_speed_factor = 0
    elif ball_bouncing:
        # Bouncing effect (forward)
        ball_y += int(bounce_vel)
        ball_x += bounce_vx
        bounce_vel += BOUNCE_GRAVITY
        bottom_limit = HEIGHT - BORDER_THICKNESS - DIVIDER_THICKNESS - BALL_HEIGHT
        if ball_y > bottom_limit:
            ball_y = bottom_limit
            if abs(bounce_vel) > BOUNCE_MIN:
                bounce_vel = -bounce_vel * BOUNCE_DAMPING
                bounce_vx = bounce_vx * BOUNCE_DAMPING
            else:
                # End bouncing, start rolling-to-stop
                ball_bouncing = False
                game_over = True
                ball_vx = 0
                bounce_vel = 0
                bounce_vx = 0
    elif game_over:
        # Ball rolls right and spins, both decelerating
        if abs(ball_vx) > 0.1:
            ball_x += ball_vx
            ball_vx = max(0, ball_vx - BALL_ROLL_DECEL)
        # Stop ball at 7/10 the screen width
        if ball_x >= WIDTH * 0.7 and ball_vx > 0:
            ball_x = WIDTH * 0.7
            ball_vx = 0
        if ball_vx > 0:
            ball_angle = (ball_angle + max(2, ball_vx)) % 360
    # Ball spinning while in play
    if background_moving and not game_over and not ball_bouncing:
        ball_angle = (ball_angle + SPIN_STEP) % 360

    # Restore background movement like before
    if (
        background_moving
        and not paused
        and not timed_quiz_active
        and not timed_quiz_feedback
        and not game_over
        and not waiting_for_replay_start
        and start_screen_stage == 2
    ):
        for i, speed in enumerate(speeds):
            offsets[i] = (offsets[i] + speed * dt * bg_speed_factor) % WIDTH

    # Handle feedback display duration
    if timed_quiz_feedback is not None:
        if time.time() - timed_quiz_feedback_time > FEEDBACK_DISPLAY_TIME:
            timed_quiz_feedback = None
            background_moving = True
            timed_quiz_last_time = time.time()  # Reset timer after feedback, not after question

    # Draw background layers
    for i, img in enumerate(layers):
        x1 = -offsets[i]
        x2 = x1 + WIDTH
        screen.blit(img, (x1, 0))
        screen.blit(img, (x2, 0))

    # Draw fade overlay ONLY over background
    if fade_direction != 0 or fade_alpha > 0:
        fade_surface.set_alpha(int(fade_alpha))
        screen.blit(fade_surface, (0, 0))

    # --- Overlay layers ---
    if start_screen_stage in (0, 1):
        # Intro screen with DrBounce and instructions
        intro_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        intro_bg.fill((0, 0, 0, 180))
        screen.blit(intro_bg, (0, 0))
        screen.blit(DRBOUNCE_IMG, (WIDTH//2 - DRBOUNCE_SIZE//2, HEIGHT//2 - DRBOUNCE_SIZE//2 - 60))
        font_intro = pygame.font.SysFont(None, 48, bold=True)
        intro_text = font_intro.render("Welcome to Flappy Learn!", True, (255, 255, 255))
        screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, HEIGHT//2 + DRBOUNCE_SIZE//2 - 20))
        font_small = pygame.font.SysFont(None, 32)
        if start_screen_stage == 0:
            press_text = font_small.render("Press UP to continue...", True, (255, 255, 0))
        else:
            press_text = font_small.render("Press UP to start!", True, (255, 255, 0))
        screen.blit(press_text, (WIDTH//2 - press_text.get_width()//2, HEIGHT//2 + DRBOUNCE_SIZE//2 + 30))

    if paused:
        # Pause overlay
        pause_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pause_bg.fill((0, 0, 0, 120))
        screen.blit(pause_bg, (0, 0))
        font_pause = pygame.font.SysFont(None, 64, bold=True)
        pause_text = font_pause.render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 32))
        font_small = pygame.font.SysFont(None, 32)
        resume_text = font_small.render("Press TAB or click pause to resume", True, (255, 255, 0))
        screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 + 32))

    if timed_quiz_active:
        # DrBounce question overlay
        quiz_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        quiz_bg.fill((0, 0, 0, 180))
        screen.blit(quiz_bg, (0, 0))
        screen.blit(DRBOUNCE_IMG, (WIDTH//2 - DRBOUNCE_SIZE//2, HEIGHT//2 - DRBOUNCE_SIZE//2 - 60))
        font_quiz = pygame.font.SysFont(None, 40, bold=True)
        question = timed_quiz_question if timed_quiz_question else ""
        question_text = font_quiz.render(question, True, (255, 255, 255))
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, HEIGHT//2 + DRBOUNCE_SIZE//2 - 20))
        font_small = pygame.font.SysFont(None, 32)
        # Show only a prompt for the user to type their answer (input field, but not the answer itself)
        input_field = font_small.render(timed_quiz_user_input, True, (255, 255, 0))
        screen.blit(input_field, (WIDTH//2 - input_field.get_width()//2, HEIGHT//2 + DRBOUNCE_SIZE//2 + 30))
        input_prompt = font_small.render("Type your answer and press Enter", True, (200, 200, 200))
        screen.blit(input_prompt, (WIDTH//2 - input_prompt.get_width()//2, HEIGHT//2 + DRBOUNCE_SIZE//2 + 60))

    if timed_quiz_feedback == 'correct':
        feedback_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        feedback_bg.fill((120, 120, 120, 180))  # grayish overlay
        screen.blit(feedback_bg, (0, 0))
        font_fb = pygame.font.SysFont(None, 80, bold=True)
        fb_text = font_fb.render("Correct!", True, (0, 180, 0))
        screen.blit(fb_text, (WIDTH//2 - fb_text.get_width()//2, HEIGHT//2 - 40))
    elif timed_quiz_feedback == 'wrong':
        feedback_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        feedback_bg.fill((120, 120, 120, 180))  # grayish overlay
        screen.blit(feedback_bg, (0, 0))
        font_fb = pygame.font.SysFont(None, 80, bold=True)
        fb_text = font_fb.render("Wrong!", True, (200, 0, 0))
        screen.blit(fb_text, (WIDTH//2 - fb_text.get_width()//2, HEIGHT//2 - 60))
        # Show the correct answer with text wrapping
        font_answer = pygame.font.SysFont(None, 48, bold=True)
        
        # Text wrapping function
        def wrap_text(text, font, max_width):
            words = text.split(' ')
            lines = []
            line = ''
            for word in words:
                test_line = line + word + ' '
                if font.size(test_line)[0] < max_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word + ' '
            if line:
                lines.append(line)
            return lines
        
        answer_text = f"The correct answer is: {timed_quiz_answer}"
        answer_lines = wrap_text(answer_text, font_answer, WIDTH - 100)  # Leave 50px margin on each side
        
        for i, line in enumerate(answer_lines):
            line_surf = font_answer.render(line.strip(), True, (255, 255, 255))
            screen.blit(line_surf, (WIDTH//2 - line_surf.get_width()//2, HEIGHT//2 + i*55))

    if game_over:
        try: 
            SERVER_URL="http://127.0.0.1:5000/"
            response = requests.post(
                SERVER_URL + "points",
                json={"id" : 1, "points" : score},
                timeout=5
            )
        except:
            args = sys.argv;
            print(f"failed {args}")
            pass
        # Game oover overlay
        over_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        over_bg.fill((0, 0, 0, 180))
        screen.blit(over_bg, (0, 0))
        font_over = pygame.font.SysFont(None, 64, bold=True)
        over_text = font_over.render("GAME OVER", True, (255, 0, 0))
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 32))
        font_small = pygame.font.SysFont(None, 32)
        replay_text = font_small.render("Press SPACE to replay or close to exit", True, (255, 255, 0))
        screen.blit(replay_text, (WIDTH//2 - replay_text.get_width()//2, HEIGHT//2 + 32))

    # Draw thick brown border (top and bottom only)
    BORDER_COLOR = (139, 69, 19)
    # Top border
    pygame.draw.rect(screen, BORDER_COLOR, (0, 0, WIDTH, BORDER_THICKNESS))
    # Bottom border
    pygame.draw.rect(screen, BORDER_COLOR, (0, HEIGHT - BORDER_THICKNESS, WIDTH, BORDER_THICKNESS))

    # --- Custom Scoreboard Drawing ---
    scoreboard_font = pygame.font.SysFont(None, 36, bold=True)
    score_font = pygame.font.SysFont(None, 32, bold=True)
    label_text = scoreboard_font.render("SCOREBOARD", True, (255, 255, 255))
    score_text = score_font.render(str(score), True, (255, 255, 255))
    # Centered positions
    label_x = (WIDTH - label_text.get_width()) // 2
    label_y = 4  # Shift up
    rect_width = 56  # Smaller width
    rect_height = 28  # Smaller height
    rect_x = (WIDTH - rect_width) // 2
    rect_y = label_y + label_text.get_height() + 2  # Shift up
    # Draw label
    screen.blit(label_text, (label_x, label_y))
    # Draw rectangle for score
    pygame.draw.rect(screen, (30, 30, 30), (rect_x, rect_y, rect_width, rect_height), border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), 2, border_radius=8)
    # Draw score centered in rectangle
    score_x = rect_x + (rect_width - score_text.get_width()) // 2
    score_y = rect_y + (rect_height - score_text.get_height()) // 2
    screen.blit(score_text, (score_x, score_y))
    # --- End Custom Scoreboard Drawing ---

    # Always define wing rects before drawing
    wing_offset_x = -WING_WIDTH // 2
    wing_offset_y = -BALL_HEIGHT // 4
    WING_Y_SHIFT = 6
    WING_X_INSET = -12  # move wings more to the right (less overlap)
    wing1_rect = rotated_wing1.get_rect(topright=(ball_x + wing_offset_x + WING_WIDTH - WING_X_INSET, ball_y + wing_offset_y + 8 + WING_Y_SHIFT - 4))
    wing2_rect = rotated_wing2.get_rect(topright=(ball_x + wing_offset_x + 4 + WING_WIDTH - WING_X_INSET, ball_y + wing_offset_y - 8 + WING_Y_SHIFT - 4))
    # Draw bottom wing (behind ball)
    screen.blit(rotated_wing2, wing2_rect.topleft)
    # Draw spinning ball (after back rim, before front rim)
    rotated_ball = pygame.transform.rotate(main_ball_img, ball_angle)
    ball_rect = rotated_ball.get_rect(center=(ball_x + BALL_WIDTH // 2, ball_y + BALL_HEIGHT // 2))
    screen.blit(rotated_ball, ball_rect.topleft)
    # Draw top wing (overlapping ball, always in front)
    screen.blit(rotated_wing1, wing1_rect.topleft)

    # --- Golden Hoops on Top Left Border ---
    for i in range(golden_hoops_left):
        x = 12 + i * (GOLDEN_HOOP_SIZE + 8)
        y = (BORDER_THICKNESS - GOLDEN_HOOP_SIZE) // 2
        screen.blit(GOLDEN_HOOP_IMG, (x, y))

    # --- Coins Drawing, Animation, and Scoring ---
    # Draw and animate coins
    for idx, (cx, cy, anim_index, anim_timer) in enumerate(coins):
        # Draw current frame
        frame = xp_coin_images[anim_index]
        screen.blit(frame, (int(cx) - COIN_RADIUS, cy - COIN_RADIUS))
        # Animate
        anim_timer += 1
        if anim_timer >= COIN_ANIM_SPEED:
            anim_index = (anim_index + 1) % XP_COIN_FRAMES
            anim_timer = 0
        coins[idx] = (cx, cy, anim_index, anim_timer)

    # Coin collision detection and scoring
    ball_center_x = ball_x + BALL_WIDTH // 2
    ball_center_y = ball_y + BALL_HEIGHT // 2
    
    for coin in coins[:]:  # Use slice to avoid modifying list while iterating
        cx, cy, anim_index, anim_timer = coin
        # Calculate distance between ball center and coin center
        dist = ((ball_center_x - cx) ** 2 + (ball_center_y - cy) ** 2) ** 0.5
        if dist < BALL_WIDTH // 2 + COIN_RADIUS:
            score += 5  # Add 5 points for each coin collected
            coins.remove(coin)

    # Move coins left with background
    if background_moving and not game_over and not ball_bouncing:
        coins = [(cx - speeds[-1] * dt * bg_speed_factor, cy, anim_index, anim_timer) 
                for (cx, cy, anim_index, anim_timer) in coins if cx > -COIN_RADIUS]

    # Spawn new coins
    if background_moving and not game_over and not ball_bouncing:
        frame_count += 1
        if frame_count % COIN_SPAWN_INTERVAL == 0:
            # Spawn coin at random position
            spawn_x = WIDTH + COIN_RADIUS
            spawn_y = random.randint(BORDER_THICKNESS + COIN_RADIUS, HEIGHT - BORDER_THICKNESS - COIN_RADIUS)
            # Start each coin at a random frame for independent animation
            coins.append((spawn_x, spawn_y, random.randint(0, XP_COIN_FRAMES-1), 0))

    prev_ball_center_y = ball_y + BALL_HEIGHT // 2
    pygame.display.flip() 
