import pygame
import random
import os
import time
import math

# Fixed window size
WIDTH, HEIGHT = 1280, 720
PLATFORM_Y_TOP = HEIGHT // 6
PLATFORM_Y_BOTTOM = 5 * HEIGHT // 6
PLATFORM_THICKNESS = 12
BALL_RADIUS = 36
BALL_START_X = 220
BALL_SPEED = 7  # Increased horizontal speed
OBSTACLE_WIDTH = 56
OBSTACLE_HEIGHT = 84
OBSTACLE_SPEED = 4

LIVES = 3
FPS = 60
GLIDE_FRAMES = 20  # Number of frames for glide animation

def get_assets_path(name : str) -> str:
    return f"./assets/games/switch_runner/{name}";

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

def run(screen):
    SPAWN_INTERVAL = 90  # Less frequent obstacles
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 44, bold=True)

# Load parallax background layers
    bg_images = []
    for layer in BG_LAYERS:
        img = pygame.image.load(BG_PATH + layer['file']).convert_alpha()
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
        bg_images.append(img)

    bg_offsets = [0.0 for _ in BG_LAYERS]

    CHARACTER_SHEET_PATH = get_assets_path("characters/animations/dude/Dude_Monster_Run_6.png")
    CHARACTER_FRAMES = 6
    character_sheet = pygame.image.load(CHARACTER_SHEET_PATH).convert_alpha()
    CHARACTER_WIDTH = character_sheet.get_width() // CHARACTER_FRAMES
    CHARACTER_HEIGHT = character_sheet.get_height()
    character_frames = [character_sheet.subsurface(pygame.Rect(i * CHARACTER_WIDTH, 0, CHARACTER_WIDTH, CHARACTER_HEIGHT)) for i in range(CHARACTER_FRAMES)]
    character_anim_index = 0
    character_anim_timer = 0
    CHARACTER_ANIM_SPEED = 4  # Lower is faster
    character_flipped = False

# Hurt animation
    HURT_SHEET_PATH = get_assets_path("characters/animations/dude/Dude_Monster_Hurt_4.png")
    HURT_FRAMES = 4
    hurt_sheet = pygame.image.load(HURT_SHEET_PATH).convert_alpha()
    hurt_width = hurt_sheet.get_width() // HURT_FRAMES
    hurt_height = hurt_sheet.get_height()
    hurt_frames = [hurt_sheet.subsurface(pygame.Rect(i * hurt_width, 0, hurt_width, hurt_height)) for i in range(HURT_FRAMES)]
    hurt_anim_index = 0
    hurt_anim_timer = 0
    HURT_ANIM_SPEED = 6
    is_hurt = False
    hurt_anim_playing = 0  # frames left

# Death animation
    DEATH_SHEET_PATH = get_assets_path("characters/animations/dude/Dude_Monster_Death_8.png")
    DEATH_FRAMES = 8
    death_sheet = pygame.image.load(DEATH_SHEET_PATH).convert_alpha()
    death_width = death_sheet.get_width() // DEATH_FRAMES
    death_height = death_sheet.get_height()
    death_frames = [death_sheet.subsurface(pygame.Rect(i * death_width, 0, death_width, death_height)) for i in range(DEATH_FRAMES)]
    death_anim_index = 0
    death_anim_timer = 0
    DEATH_ANIM_SPEED = 6
    death_anim_playing = False
    character_visible = True

# Ball state
    xp = 0  # Player XP
    target_lane = 1  # Start at bottom platform
    ball_lane = 1
    ball_angle = 0
    lives = LIVES
    ball_glide = 0  # 0 if not gliding, >0 if gliding
    ball_y = PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
    ball_x = BALL_START_X
    ANCHOR_X = int(WIDTH * 0.4)  # Ball stays at 40% of the screen

# Obstacles: list of (x, lane, frame_index)
    obstacles = []
    pickables = []  # List of (x, lane, anim_index, anim_timer)
    PICKABLE_RADIUS = 24
    PICKABLE_COLOR = (80, 220, 120)
    PICKABLE_SPAWN_INTERVAL = SPAWN_INTERVAL * 3  # Less frequent than obstacles
    frame_count = 0
    game_over = False

# Load player and entity images for story/dialogue
    PLAYER_IMAGE_PATH = get_assets_path("characters/select/Dude_Monster.png")
    ENTITY_IMAGE_PATH = get_assets_path("characters/entity/download (1).jpeg")
    player_img = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
    entity_img = pygame.image.load(ENTITY_IMAGE_PATH).convert_alpha()
    player_img = pygame.transform.scale(player_img, (220, 220))
    entity_img = pygame.transform.scale(entity_img, (220, 300))

# Story/dialogue sequence
    story_dialogue = [
        ("entity", "I have kidnapped Ursula and I will not bring her back."),
        ("player", "What, who are you?"),
        ("entity", "I am, the Entity."),
        ("player", "Give back Ursula right now."),
        ("entity", "I will if you play a little game with me. Answer this question, Will you play the game or not?")
    ]
    story_mode = True
    story_index = 0
    story_choice = None  # None, 'yes', or 'no'
    choice_selected = 0  # 0 for Yes, 1 for No
    SPAWN_INTERVAL_SLOW = 90
    SPAWN_INTERVAL_FAST = 45

# Utility function to draw an image with rounded corners
    def blit_rounded(surface, image, pos, radius=40):
        size = image.get_size()
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255,255,255,255), (0,0,*size), border_radius=radius)
        img_copy = image.copy()
        img_copy.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(img_copy, pos)

# Utility to draw a transparent bubble over the player when invincible
    def blit_transparent_bubble(surface, bubble_img, center, scale=2.2, alpha=140):
        # Scale bubble
        size = int(BALL_RADIUS * 2 * scale)
        bubble = pygame.transform.smoothscale(bubble_img, (size, size)).copy()
        bubble.set_alpha(alpha)
        x = center[0] - size // 2
        y = center[1] - size // 2
        surface.blit(bubble, (x, y))

# Powerup settings
    POWERUP_RADIUS = 28
    POWERUP_COLOR = (255, 215, 0)
    POWERUP_TYPE_INVINCIBLE = 'invincible'
    POWERUP_TYPE_HEART = 'heart'
    powerups = []  # List of (x, lane, type)

# Invincibility state
    invincible = False
    invincible_timer = 0

# Math encounter settings
    MATH_INTERVALS = [15, 17, 21, 29, 33, 46, 54, 67]
    next_math_time = time.time() + random.choice(MATH_INTERVALS)
    math_mode = False
    math_question = None
    math_options = []
    math_correct_index = 0
    math_selected = 0
    math_feedback = ''
    math_feedback_timer = 0
    math_intensity_mult = 1.0
    MATH_LAUGH_DURATION = 1.2

# XP Coin Animation
    XP_COIN_FRAMES = 6
    XP_COIN_PATH = get_assets_path("objects/xp_coin")
    xp_coin_images = []
    for i in range(1, XP_COIN_FRAMES + 1):
        img_path = os.path.join(XP_COIN_PATH, f'Coin_{i:02d}.png')
        img = pygame.image.load(img_path).convert_alpha()
        img = pygame.transform.scale(img, (PICKABLE_RADIUS * 2, PICKABLE_RADIUS * 2))
        xp_coin_images.append(img)
    PICKABLE_ANIM_SPEED = 6  # frames per animation step

# Powerup and Life Images
    BUBBLE_PATH = get_assets_path("objects/Bubble.png")
    LIFE_PATH = get_assets_path("objects/Life.png")
    bubble_img = pygame.image.load(BUBBLE_PATH).convert_alpha()
    bubble_img = pygame.transform.scale(bubble_img, (POWERUP_RADIUS * 2, POWERUP_RADIUS * 2))
    life_img = pygame.image.load(LIFE_PATH).convert_alpha()
    life_img = pygame.transform.scale(life_img, (60, 60))

# Spikes obstacle sprite sheet
    SPIKES_PATH = get_assets_path("objects/Spikes.png")
    SPIKES_FRAMES = 4
    spikes_sheet = pygame.image.load(SPIKES_PATH).convert_alpha()
    spikes_width = spikes_sheet.get_width() // SPIKES_FRAMES
    spikes_height = spikes_sheet.get_height()
    spikes_frames = [spikes_sheet.subsurface(pygame.Rect(i * spikes_width, 0, spikes_width, spikes_height)) for i in range(SPIKES_FRAMES)]

    running = True
    while running:
        now = time.time()
        # Handle invincibility timer
        if invincible and not story_mode and not math_mode:
            if time.time() > invincible_timer:
                invincible = False
        # Math encounter trigger
        if not story_mode and not math_mode and not game_over and now > next_math_time:
            math_mode = True
            # Generate math question
            a, b = random.randint(2, 12), random.randint(2, 12)
            op = random.choice(['+', '-', '*'])
            if op == '+':
                answer = a + b
            elif op == '-':
                answer = a - b
            else:
                answer = a * b
            wrong1 = answer + random.choice([-3, -2, -1, 1, 2, 3])
            wrong2 = answer + random.choice([-6, -4, 4, 6])
            options = [answer, wrong1, wrong2]
            random.shuffle(options)
            math_correct_index = options.index(answer)
            math_question = (f"Answer this question correct and you will get a reward.",
                            f"What is {a} {op} {b}?")
            math_options = options
            math_selected = 0
            math_feedback = ''
            math_feedback_timer = 0
        if math_mode:
            screen.fill((30, 30, 40))
            # Draw entity with rounded corners at top center
            blit_rounded(screen, entity_img, (WIDTH//2 - 110, 60), radius=15)
            # Draw question box (taller to fit all text)
            rect_w = 1000
            rect_h = 240
            rect_x = WIDTH//2 - rect_w//2
            rect_y = 260
            pygame.draw.rect(screen, (40, 40, 60), (rect_x, rect_y, rect_w, rect_h), border_radius=20)
            pygame.draw.rect(screen, (100, 100, 160), (rect_x, rect_y, rect_w, rect_h), 4, border_radius=20)
            # Render and center both lines inside the rectangle
            question_font = pygame.font.SysFont('arial', 44, bold=True)
            qsurf1 = question_font.render(math_question[0], True, (255,255,255))
            qsurf2 = question_font.render(math_question[1], True, (255,255,255))
            q1_y = rect_y + 28
            q2_y = q1_y + qsurf1.get_height() + 10
            screen.blit(qsurf1, (rect_x + (rect_w - qsurf1.get_width())//2, q1_y))
            screen.blit(qsurf2, (rect_x + (rect_w - qsurf2.get_width())//2, q2_y))
            # Move options further down
            options_y = q2_y + qsurf2.get_height() + 32
            for i, opt in enumerate(math_options):
                color = (255,255,0) if i == math_selected else (200,200,200)
                osurf = font.render(str(opt), True, color)
                screen.blit(osurf, (WIDTH//2 - 120 + i*120, options_y))
            # Feedback
            if math_feedback:
                if 'Wrong' in math_feedback:
                    fsurf = font.render(math_feedback, True, (255, 99, 71))
                    screen.blit(fsurf, (WIDTH//2 - fsurf.get_width()//2, 500))
                    # Show Hahahahah after answer for a moment
                    if time.time() > math_feedback_timer:
                        laugh_font = pygame.font.SysFont('arial', 54, bold=True)
                        laugh_text = laugh_font.render('Hahahahah!', True, (255, 99, 71))
                        screen.blit(laugh_text, (WIDTH//2 - laugh_text.get_width()//2, 570))
                        pygame.display.flip()
                        pygame.time.delay(int(MATH_LAUGH_DURATION * 1000))
                        # End math mode, reset timer
                        math_mode = False
                        next_math_time = time.time() + random.choice(MATH_INTERVALS)
                        continue
                else:
                    fsurf = font.render(math_feedback, True, (80, 220, 120))
                    screen.blit(fsurf, (WIDTH//2 - fsurf.get_width()//2, 500))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and not math_feedback:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        math_selected = (math_selected - 1) % 3
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        math_selected = (math_selected + 1) % 3
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if math_selected == math_correct_index:
                            # Correct
                            math_feedback = 'Correct!'
                            xp_gain = math.ceil(xp / 10) + 7
                            xp += xp_gain
                            # Randomly choose prize: invincibility or heart
                            prize_type = random.choice([POWERUP_TYPE_INVINCIBLE, POWERUP_TYPE_HEART])
                            lane = random.randint(0, 1)
                            powerup_x = WIDTH
                            while True:
                                overlap = False
                                for ox, olane, frame_idx in obstacles:
                                    if olane == lane and abs(ox - powerup_x) < OBSTACLE_WIDTH + POWERUP_RADIUS * 2:
                                        overlap = True
                                        break
                                if not overlap:
                                    break
                                powerup_x += OBSTACLE_WIDTH + POWERUP_RADIUS * 2
                                if powerup_x > WIDTH + 300:  # Don't go too far off screen
                                    break
                            if prize_type == POWERUP_TYPE_INVINCIBLE:
                                duration = random.randint(5, 13)
                                powerups.append((powerup_x, lane, POWERUP_TYPE_INVINCIBLE, duration))
                            else:
                                powerups.append((powerup_x, lane, POWERUP_TYPE_HEART))
                        else:
                            # Wrong
                            math_feedback = f'Wrong answer. The answer is {math_options[math_correct_index]}'
                            xp = max(0, xp - 7)
                        math_feedback_timer = time.time() + 1.5
                        # Increase intensity
                        math_intensity_mult *= 1.05
                        # Increase obstacle speed and decrease spawn interval
                        OBSTACLE_SPEED = int(OBSTACLE_SPEED * math_intensity_mult)
                        SPAWN_INTERVAL = max(20, int(SPAWN_INTERVAL / math_intensity_mult))
                elif event.type == pygame.KEYDOWN and math_feedback and 'Wrong' not in math_feedback and time.time() > math_feedback_timer:
                    # End math mode, reset timer
                    math_mode = False
                    next_math_time = time.time() + random.choice(MATH_INTERVALS)
            continue
        if story_mode:
            screen.fill((30, 30, 40))
            # Draw player and entity images
            screen.blit(player_img, (80, HEIGHT//2 - 110))
            blit_rounded(screen, entity_img, (WIDTH - 300, HEIGHT//2 - 150), radius=15)
            # Draw dialogue box
            pygame.draw.rect(screen, (40, 40, 60), (200, HEIGHT - 220, WIDTH - 400, 160), border_radius=20)
            pygame.draw.rect(screen, (100, 100, 160), (200, HEIGHT - 220, WIDTH - 400, 160), 4, border_radius=20)
            # Show dialogue or choice
            if story_index < len(story_dialogue):
                who, text = story_dialogue[story_index]
                name = "Entity" if who == "entity" else "You"
                name_color = (255, 99, 71) if who == "entity" else (99, 200, 255)
                name_surf = font.render(name, True, name_color)
                screen.blit(name_surf, (220, HEIGHT - 210))
                # Render text (wrap if needed)
                words = text.split(' ')
                lines = []
                line = ''
                for word in words:
                    test_line = line + word + ' '
                    if font.size(test_line)[0] < WIDTH - 440:
                        line = test_line
                    else:
                        lines.append(line)
                        line = word + ' '
                lines.append(line)
                for i, l in enumerate(lines):
                    txt_surf = font.render(l.strip(), True, (255,255,255))
                    screen.blit(txt_surf, (220, HEIGHT - 160 + i*44))
                # Prompt
                prompt = font.render("Press SPACE or ENTER...", True, (180,180,180))
                screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 60))
            else:
                # Choice screen
                question = font.render("Will you play the game or not?", True, (255,255,255))
                screen.blit(question, (WIDTH//2 - question.get_width()//2, HEIGHT - 200))
                yes_color = (255,255,0) if choice_selected == 0 else (200,200,200)
                no_color = (255,255,0) if choice_selected == 1 else (200,200,200)
                yes_surf = font.render("Yes", True, yes_color)
                no_surf = font.render("No", True, no_color)
                screen.blit(yes_surf, (WIDTH//2 - 120, HEIGHT - 120))
                screen.blit(no_surf, (WIDTH//2 + 40, HEIGHT - 120))
                prompt = font.render("Use LEFT/RIGHT and ENTER/SPACE", True, (180,180,180))
                screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 60))
            pygame.display.flip()
            # Handle story input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if story_index < len(story_dialogue):
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            story_index += 1
                    else:
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            choice_selected = 0
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            choice_selected = 1
                        elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            story_choice = 'yes' if choice_selected == 0 else 'no'
                            story_mode = False
                            # If 'no', show evil laugh for a moment before starting game
                            if story_choice == 'no':
                                laugh_font = pygame.font.SysFont('arial', 60, bold=True)
                                laugh_text = laugh_font.render('Wrong choice, Hahahahahahah', True, (255, 99, 71))
                                screen.fill((30, 30, 40))
                                blit_rounded(screen, entity_img, (WIDTH//2 - 110, HEIGHT//2 - 150), radius=15)
                                screen.blit(laugh_text, (WIDTH//2 - laugh_text.get_width()//2, HEIGHT - 200))
                                pygame.display.flip()
                                pygame.time.delay(1800)
                            # Set obstacle frequency
                            SPAWN_INTERVAL = SPAWN_INTERVAL_FAST if story_choice == 'no' else SPAWN_INTERVAL_SLOW
            continue
        screen.fill((30, 30, 40))
        # Draw parallax background
        for i, layer in enumerate(BG_LAYERS):
            speed = layer['speed']
            bg_offsets[i] = (bg_offsets[i] - speed) % WIDTH
            x1 = int(bg_offsets[i])
            x2 = x1 - WIDTH
            screen.blit(bg_images[i], (x1, 0))
            screen.blit(bg_images[i], (x2, 0))
        # Show warning 5 seconds before entity appears
        if not story_mode and not math_mode and not game_over:
            time_to_entity = next_math_time - now
            if 0 < time_to_entity <= 5:
                warn_font = pygame.font.SysFont('arial', 36, bold=True)
                warn_text = warn_font.render('Warning: The Entity will appear soon!', True, (255, 99, 71))
                screen.blit(warn_text, (WIDTH//2 - warn_text.get_width()//2, 20))
        # Ball horizontal movement
        if not game_over:
            ball_x += BALL_SPEED
            if ball_x > ANCHOR_X:
                # Keep the ball at anchor, move obstacles left instead
                shift = ball_x - ANCHOR_X
                ball_x = ANCHOR_X
                obstacles = [(ox - shift, olane, frame_idx) for ox, olane, frame_idx in obstacles]
                pickables = [(px - shift, plane, anim_index, anim_timer) for (px, plane, anim_index, anim_timer) in pickables]
                powerups = [(ppx - shift, pplane, ptype, *pdata) for (ppx, pplane, ptype, *pdata) in powerups]
        # Draw platforms as lines
        pygame.draw.line(screen, (80, 80, 120), (0, PLATFORM_Y_TOP), (WIDTH, PLATFORM_Y_TOP), PLATFORM_THICKNESS)
        pygame.draw.line(screen, (80, 80, 120), (0, PLATFORM_Y_BOTTOM), (WIDTH, PLATFORM_Y_BOTTOM), PLATFORM_THICKNESS)
        # Ball glide logic
        if ball_glide > 0:
            start_y = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2 if ball_lane == 0 else PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
            end_y = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2 if target_lane == 0 else PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
            t = (GLIDE_FRAMES - ball_glide + 1) / GLIDE_FRAMES
            ball_y = int(start_y + (end_y - start_y) * t)
            ball_glide -= 1
            if ball_glide == 0:
                ball_lane = target_lane
                ball_y = end_y
                character_flipped = not character_flipped  # Flip character on switch
        else:
            ball_y = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2 if ball_lane == 0 else PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
        # Draw character run/hurt/death animation instead of ball
        if character_visible:
            # Draw invincibility bubble if active
            if invincible:
                blit_transparent_bubble(screen, bubble_img, (int(ball_x), ball_y), scale=2.2, alpha=140)
            if death_anim_playing:
                if death_anim_index < DEATH_FRAMES:
                    death_anim_timer += 1
                    if death_anim_timer >= DEATH_ANIM_SPEED:
                        death_anim_index += 1
                        death_anim_timer = 0
                    if death_anim_index < DEATH_FRAMES:
                        frame = death_frames[death_anim_index]
                        frame_scaled = pygame.transform.scale(frame, (BALL_RADIUS * 2, BALL_RADIUS * 2))
                        if character_flipped:
                            frame_scaled = pygame.transform.flip(frame_scaled, False, True)
                        screen.blit(frame_scaled, (int(ball_x) - BALL_RADIUS, ball_y - BALL_RADIUS))
                if death_anim_index >= DEATH_FRAMES:
                    character_visible = False
                    death_anim_playing = False
            elif is_hurt:
                hurt_anim_timer += 1
                if hurt_anim_timer >= HURT_ANIM_SPEED:
                    hurt_anim_index += 1
                    hurt_anim_timer = 0
                    if hurt_anim_index >= HURT_FRAMES:
                        is_hurt = False
                        hurt_anim_index = 0
                if hurt_anim_index < HURT_FRAMES:
                    frame = hurt_frames[hurt_anim_index]
                    frame_scaled = pygame.transform.scale(frame, (BALL_RADIUS * 2, BALL_RADIUS * 2))
                    if character_flipped:
                        frame_scaled = pygame.transform.flip(frame_scaled, False, True)
                    screen.blit(frame_scaled, (int(ball_x) - BALL_RADIUS, ball_y - BALL_RADIUS))
            else:
                character_anim_timer += 1
                if character_anim_timer >= CHARACTER_ANIM_SPEED:
                    character_anim_index = (character_anim_index + 1) % CHARACTER_FRAMES
                    character_anim_timer = 0
                frame = character_frames[character_anim_index]
                frame_scaled = pygame.transform.scale(frame, (BALL_RADIUS * 2, BALL_RADIUS * 2))
                if character_flipped:
                    frame_scaled = pygame.transform.flip(frame_scaled, False, True)  # Vertical flip
                screen.blit(frame_scaled, (int(ball_x) - BALL_RADIUS, ball_y - BALL_RADIUS))
        # (Removed ball spin effect)
        # Draw and animate pickables
        for idx, (px, plane, anim_index, anim_timer) in enumerate(pickables):
            if plane == 0:
                py = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2
            else:
                py = PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
            # Draw current frame
            frame = xp_coin_images[anim_index]
            screen.blit(frame, (int(px) - PICKABLE_RADIUS, py - PICKABLE_RADIUS))
            # Animate
            anim_timer += 1
            if anim_timer >= PICKABLE_ANIM_SPEED:
                anim_index = (anim_index + 1) % XP_COIN_FRAMES
                anim_timer = 0
            pickables[idx] = (px, plane, anim_index, anim_timer)
        # Draw powerups
        for ppx, pplane, ptype, *pdata in powerups:
            if pplane == 0:
                ppy = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2
            else:
                ppy = PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
            if ptype == POWERUP_TYPE_INVINCIBLE:
                screen.blit(bubble_img, (int(ppx) - POWERUP_RADIUS, ppy - POWERUP_RADIUS))
            elif ptype == POWERUP_TYPE_HEART:
                screen.blit(life_img, (int(ppx) - POWERUP_RADIUS, ppy - POWERUP_RADIUS))
        # Draw obstacles
        for ox, olane, frame_idx in obstacles:
            if olane == 0:
                oy = PLATFORM_Y_TOP + PLATFORM_THICKNESS // 2
                spike_img = pygame.transform.scale(spikes_frames[frame_idx], (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
                spike_img = pygame.transform.flip(spike_img, False, True)  # Flip vertically for top lane
            else:
                oy = PLATFORM_Y_BOTTOM - OBSTACLE_HEIGHT - PLATFORM_THICKNESS // 2
                spike_img = pygame.transform.scale(spikes_frames[frame_idx], (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
            screen.blit(spike_img, (ox, oy))
        # Draw lives
        for i in range(lives):
            x = WIDTH - 80 - i * 64
            y = 80
            if invincible:
                # Optionally tint or animate if invincible
                screen.blit(life_img, (x - 30, y - 30))
            else:
                screen.blit(life_img, (x - 30, y - 30))
        # Game over
        if game_over:
            # If death animation is playing, wait for it to finish
            if death_anim_playing:
                pygame.display.flip()
                continue
            # If character is not visible (death animation finished), show Game Over
            if not character_visible:
                over_text = font.render('Game Over!', True, (255,255,255))
                screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 30))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                continue
        # Draw XP
        xp_surf = font.render(f'XP: {xp}', True, (255, 255, 100))
        screen.blit(xp_surf, (40, 40))
        # Move obstacles
        obstacles = [(ox - OBSTACLE_SPEED, olane, frame_idx) for ox, olane, frame_idx in obstacles if ox > -OBSTACLE_WIDTH]
        pickables = [(px - OBSTACLE_SPEED, plane, anim_index, anim_timer) for (px, plane, anim_index, anim_timer) in pickables if px > -PICKABLE_RADIUS]
        powerups = [(ppx - OBSTACLE_SPEED, pplane, ptype, *pdata) for (ppx, pplane, ptype, *pdata) in powerups if ppx > -POWERUP_RADIUS]
        # Spawn new obstacles
        frame_count += 1
        if frame_count % SPAWN_INTERVAL == 0:
            lane = random.randint(0, 1)
            frame_idx = random.randint(0, SPIKES_FRAMES - 1)
            obstacles.append((WIDTH, lane, frame_idx))
        # Spawn new pickables
        if frame_count % PICKABLE_SPAWN_INTERVAL == 0:
            lane = random.randint(0, 1)
            # Check for overlap with obstacles in the same lane
            overlap = False
            for ox, olane, frame_idx in obstacles:
                if olane == lane and abs(ox - WIDTH) < OBSTACLE_WIDTH + PICKABLE_RADIUS * 2:
                    overlap = True
                    break
            if not overlap:
                # Start each pickable at a random frame for independent animation
                pickables.append((WIDTH, lane, random.randint(0, XP_COIN_FRAMES-1), 0))
        # Collision detection (only when not gliding)
        if ball_glide == 0:
            for ox, olane, frame_idx in obstacles:
                if invincible:
                    continue
                if olane == ball_lane:
                    if olane == 0:
                        ball_center = (int(ball_x), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                        obs_rect = pygame.Rect(ox, PLATFORM_Y_TOP + PLATFORM_THICKNESS // 2, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                    else:
                        ball_center = (int(ball_x), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                        obs_rect = pygame.Rect(ox, PLATFORM_Y_BOTTOM - OBSTACLE_HEIGHT - PLATFORM_THICKNESS // 2, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                    cx, cy = ball_center
                    rx, ry, rw, rh = obs_rect
                    closest_x = max(rx, min(cx, rx + rw))
                    closest_y = max(ry, min(cy, ry + rh))
                    dist = ((cx - closest_x) ** 2 + (cy - closest_y) ** 2) ** 0.5
                    if dist < BALL_RADIUS:
                        if not is_hurt and not death_anim_playing:
                            if lives > 1:
                                is_hurt = True
                                hurt_anim_index = 0
                                hurt_anim_timer = 0
                            lives -= 1
                            obstacles.remove((ox, olane, frame_idx))
                            if lives <= 0:
                                death_anim_playing = True
                                death_anim_index = 0
                                death_anim_timer = 0
                                game_over = True
                            break
            # Pickable collision
            for pick in pickables[:]:
                px, plane, anim_index, anim_timer = pick
                if plane == ball_lane:
                    if plane == 0:
                        ball_center = (int(ball_x), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                        pick_center = (int(px), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                    else:
                        ball_center = (int(ball_x), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                        pick_center = (int(px), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                    dist = ((ball_center[0] - pick_center[0]) ** 2 + (ball_center[1] - pick_center[1]) ** 2) ** 0.5
                    if dist < BALL_RADIUS + PICKABLE_RADIUS:
                        xp += 15
                        pickables.remove(pick)
            # Powerup collision
            for powerup in powerups[:]:
                ppx, pplane, ptype, *pdata = powerup
                if pplane == ball_lane:
                    if pplane == 0:
                        ball_center = (int(ball_x), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                        powerup_center = (int(ppx), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                    else:
                        ball_center = (int(ball_x), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                        powerup_center = (int(ppx), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                    dist = ((ball_center[0] - powerup_center[0]) ** 2 + (ball_center[1] - powerup_center[1]) ** 2) ** 0.5
                    if dist < BALL_RADIUS + POWERUP_RADIUS:
                        if ptype == POWERUP_TYPE_INVINCIBLE:
                            duration = pdata[0] if pdata else 7
                            invincible = True
                            invincible_timer = time.time() + duration
                        elif ptype == POWERUP_TYPE_HEART:
                            lives = min(lives + 1, 9)
                        powerups.remove(powerup)
        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and ball_glide == 0:
                    target_lane = 1 - ball_lane
                    ball_glide = GLIDE_FRAMES
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over and ball_glide == 0:
                target_lane = 1 - ball_lane
                ball_glide = GLIDE_FRAMES
        pygame.display.flip()
        clock.tick(FPS)
