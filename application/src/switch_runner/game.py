import sys
import os

# Ensure the parent directory is in sys.path for absolute imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enum import Enum
import pygame
import random
import time
import math
import glob
import requests
import json
import pygame.mixer

from switch_runner.constants import *
from switch_runner.helper import *

class SwitchRunnerGame():
    def __init__(self):
        self.setup_background();
        self.setup_character();
        self.setup_death();
        self.setup_hurt();
        self.setup_ball_state();
        self.setup_obstacles();
        self.setup_maths();
        self.setup_entities();
        self.setup_spikes();
        self.setup_story();
        self.setup_state();
        self.setup_xp_coin();
        # Initialize question/AI state
        self.question_mode = False
        self.question_data = None
        self.user_text = ''
        self.question_feedback = ''
        self.question_feedback_timer = 0
        self.answer_checking = False
        self.show_entity_decision = False
        self.entity_decision_time = 0
        self.ai_thread = None
        self.ai_result = None
        self.next_question_time = time.time() + random.choice(MATH_INTERVALS)
        # Play background music
        music_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '../assets/audio/Lukrembo.mp3'))
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # Loop forever
        except Exception as e:
            print(f"[ERROR] Could not play background music: {e}")
    
    def setup_background(self) :
        self.bg_images = []
        for layer in BG_LAYERS:
            img = pygame.image.load(BG_PATH + layer['file']).convert_alpha()
            img = pygame.transform.scale(img, (WIDTH, HEIGHT))
            self.bg_images.append(img)

        self.bg_offsets = [0.0 for _ in BG_LAYERS]

    def setup_character(self):
        character_sheet = pygame.image.load(CHARACTER_SHEET_PATH).convert_alpha()
        CHARACTER_WIDTH = character_sheet.get_width() // CHARACTER_FRAMES
        CHARACTER_HEIGHT = character_sheet.get_height()
        self.character_frames = [character_sheet.subsurface(pygame.Rect(i * CHARACTER_WIDTH, 0, CHARACTER_WIDTH, CHARACTER_HEIGHT)) for i in range(CHARACTER_FRAMES)]
        self.character_anim_index = 0
        self.character_anim_timer = 0
        self.character_flipped = False
        self.character_visible = True

    def setup_hurt(self):
        hurt_sheet = pygame.image.load(HURT_SHEET_PATH).convert_alpha()
        hurt_width = hurt_sheet.get_width() // HURT_FRAMES
        hurt_height = hurt_sheet.get_height()
        self.hurt_frames = [hurt_sheet.subsurface(pygame.Rect(i * hurt_width, 0, hurt_width, hurt_height)) for i in range(HURT_FRAMES)]
        self.hurt_anim_index = 0
        self.hurt_anim_timer = 0
        self.is_hurt = False
        self.hurt_anim_playing = 0  # frames left

    def setup_death(self):
        death_sheet = pygame.image.load(DEATH_SHEET_PATH).convert_alpha()
        death_width = death_sheet.get_width() // DEATH_FRAMES
        death_height = death_sheet.get_height()
        self.death_frames = [death_sheet.subsurface(pygame.Rect(i * death_width, 0, death_width, death_height)) for i in range(DEATH_FRAMES)]
        self.death_anim_index = 0
        self.death_anim_timer = 0
        self.death_anim_playing = False

    def setup_obstacles(self):
        self.obstacles = []
        self.pickables = []  # List of (x, lane, anim_index, anim_timer)
        self.frame_count = 0
        self.obstacle_speed = 4;
        self.spawn_interval = 90  # Less frequent Obstacles

    def setup_state(self):
        self.game_over = False;
        self.story_mode = True;

        self.powerups = []  # List of (x, lane, type)
        self.invincible = False
        self.invincible_timer = 0
        self.story_dialogue = STARTING_DIALOGUE

    def setup_ball_state(self):
        self.xp = 0  # Player XP
        self.target_lane = 1  # Start at bottom platform
        self.ball_lane = 1
        self.ball_angle = 0
        self.lives = LIVES
        self.ball_glide = 0  # 0 if not gliding, >0 if gliding
        self.ball_y = PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
        self.ball_x = BALL_START_X

    def setup_maths(self):
        self.next_math_time = time.time() + random.choice(MATH_INTERVALS)
        self.math_question = None
        self.math_options = []
        self.math_correct_index = 0
        self.math_selected = 0
        self.math_feedback = ''
        self.math_feedback_timer = 0
        self.math_intensity_mult = 1.0
    
    def setup_entities(self):
        self.player_img = pygame.image.load(PLAYER_IMAGE_PATH).convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (220, 220))
        self.entity_img = pygame.image.load(ENTITY_IMAGE_PATH).convert_alpha()
        self.entity_img = pygame.transform.scale(self.entity_img, (220, 300))
        self.bubble_img = pygame.image.load(BUBBLE_PATH).convert_alpha()
        self.bubble_img = pygame.transform.scale(self.bubble_img, (POWERUP_RADIUS * 2, POWERUP_RADIUS * 2))
        self.life_img = pygame.image.load(LIFE_PATH).convert_alpha()
        self.life_img = pygame.transform.scale(self.life_img, (60, 60))

    def setup_story(self):
        self.story_index = 0
        self.story_choice = None  # None, 'yes', or 'no'
        self.choice_selected = 0  # 0 for Yes, 1 for No

    def setup_xp_coin(self):
        self.xp_coin_images = []
        for i in range(1, XP_COIN_FRAMES + 1):
            img_path = os.path.join(XP_COIN_PATH, f'Coin_{i:02d}.png')
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (PICKABLE_RADIUS * 2, PICKABLE_RADIUS * 2))
            self.xp_coin_images.append(img)

    def setup_spikes(self):
        spikes_sheet = pygame.image.load(SPIKES_PATH).convert_alpha()
        spikes_width = spikes_sheet.get_width() // SPIKES_FRAMES
        spikes_height = spikes_sheet.get_height()
        self.spikes_frames = [spikes_sheet.subsurface(pygame.Rect(i * spikes_width, 0, spikes_width, spikes_height)) for i in range(SPIKES_FRAMES)]

    def ai_check_answer(self, question, correct_answer, user_answer):
        HF_TOKEN = ""  # Paste your Hugging Face API token here
        API_URL = "https://router.huggingface.co/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
        }
        prompt = (
            f"Question: {question}\n"
            f"User's answer: {user_answer}\n"
            f"Correct answer: {correct_answer}\n"
            "Is the user's answer correct? Reply only Yes or No"
        )
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "model": "deepseek-ai/DeepSeek-R1:novita"
        }
        try:
            resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            if content.lower().startswith("yes"):
                return True, "Correct!"
            return False, f"Wrong! The answer is {correct_answer}"
        except Exception as e:
            print(f"[ERROR] AI check failed: {e}")
            return False, f"Wrong! The answer is {correct_answer} (AI check failed)"

    def generate_math_question(self):
        """Generate a random math question when no JSON questions are available"""
        import random
        import operator
        
        # Define operations and their symbols
        operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
        
        # Choose operation (avoid division for simplicity)
        op_symbol = random.choice(['+', '-', '*'])
        op_func = operations[op_symbol]
        
        # Generate numbers based on operation
        if op_symbol == '+':
            a = random.randint(1, 50)
            b = random.randint(1, 50)
        elif op_symbol == '-':
            a = random.randint(10, 100)
            b = random.randint(1, a)  # Ensure positive result
        else:  # multiplication
            a = random.randint(2, 12)
            b = random.randint(2, 12)
        
        # Calculate answer
        answer = op_func(a, b)
        
        # Format question
        question = f"What is {a} {op_symbol} {b}?"
        
        return {"question": question, "answer": str(int(answer))}

    def check_math_answer(self, question, correct_answer, user_answer):
        """Check math answer without AI - simple string comparison"""
        try:
            # Try to convert user answer to number for comparison
            user_num = float(user_answer.strip())
            correct_num = float(correct_answer.strip())
            if abs(user_num - correct_num) < 0.01:  # Allow small floating point differences
                return True, "Correct!"
            else:
                return False, f"Wrong! The answer is {correct_answer}"
        except ValueError:
            # If conversion fails, do string comparison
            if user_answer.strip().lower() == correct_answer.strip().lower():
                return True, "Correct!"
            else:
                return False, f"Wrong! The answer is {correct_answer}"

    def check_json_answer_locally(self, question, correct_answer, user_answer):
        """Check JSON answer locally without AI - case-insensitive string comparison"""
        # Clean and normalize both answers
        user_clean = user_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()
        
        if user_clean == correct_clean:
            return True, "Correct!"
        else:
            return False, f"Hahahahahah wrong answer! The correct answer is {correct_answer}"

    # Remove math_encounter_trigger and all uses of self.math_mode, self.math_question, self.math_options, etc.


    def run(self,screen):
        clock = pygame.time.Clock()
        font = pygame.font.SysFont('roboto', 44, bold=True)

        running = True
        while running:
            self.now = time.time()
            # Handle invincibility timer
            if self.invincible and not self.story_mode and not self.question_mode:
                if time.time() > self.invincible_timer:
                    self.invincible = False
            # Question encounter trigger
            if not self.story_mode and not self.question_mode and not self.game_over and self.now > self.next_question_time:
                self.question_mode = True
                # Use absolute path for jsons directory
                json_dir = os.path.join(os.path.dirname(__file__), '../jsons')
                json_files = glob.glob(os.path.join(json_dir, '*.json'))
                valid_questions = []
                for chosen_file in json_files:
                    try:
                        with open(chosen_file, 'r', encoding='utf-8') as f:
                            questions = json.load(f)
                        if isinstance(questions, list) and questions:
                            valid_questions.extend(questions)
                    except Exception as e:
                        print(f"[ERROR] Could not load questions from {chosen_file}: {e}")
                        continue
                if valid_questions:
                    self.question_data = random.choice(valid_questions)
                    self.is_math_question = False
                else:
                    # Generate a math question as fallback
                    self.question_data = self.generate_math_question()
                    self.is_math_question = True
                self.user_text = ''
                self.question_feedback = ''
                self.question_feedback_timer = 0
                self.answer_checking = False
                self.show_entity_decision = False
                self.entity_decision_time = 0
                self.ai_result = None
            if self.question_mode:
                print(f"[DEBUG] In question_mode. user_text='{self.user_text}' answer_checking={self.answer_checking} show_entity_decision={self.show_entity_decision}")
                screen.fill((30, 30, 40))
                # Draw entity with rounded corners at top center
                blit_rounded(screen, self.entity_img, (WIDTH//2 - 110, 60), radius=15)
                # Draw question box
                rect_w = 1000
                rect_h = 240
                rect_x = WIDTH//2 - rect_w//2
                rect_y = 260
                pygame.draw.rect(screen, (40, 40, 60), (rect_x, rect_y, rect_w, rect_h), border_radius=20)
                pygame.draw.rect(screen, (100, 100, 160), (rect_x, rect_y, rect_w, rect_h), 4, border_radius=20)
                # Render and wrap question text
                question_font = pygame.font.SysFont('arial', 38, bold=True)
                def wrap_text(text, font, max_width):
                    words = text.split(' ')
                    lines = []
                    line = ''
                    for word in words:
                        test_line = line + word + ' '
                        if font.size(test_line)[0] < max_width:
                            line = test_line
                        else:
                            lines.append(line)
                            line = word + ' '
                    lines.append(line)
                    return lines
                question_lines = wrap_text(self.question_data['question'], question_font, rect_w - 80)
                for i, l in enumerate(question_lines):
                    qsurf = question_font.render(l.strip(), True, (255,255,255))
                    screen.blit(qsurf, (rect_x + 40, rect_y + 40 + i*44))
                # Draw input box
                input_rect = pygame.Rect(rect_x + 60, rect_y + 120, rect_w - 120, 48)
                pygame.draw.rect(screen, (60, 60, 90), input_rect, border_radius=12)
                pygame.draw.rect(screen, (180, 180, 220), input_rect, 2, border_radius=12)
                input_font = pygame.font.SysFont('arial', 32)
                input_surf = input_font.render(self.user_text, True, (255,255,0))
                screen.blit(input_surf, (input_rect.x + 10, input_rect.y + 8))
                # Feedback
                if self.answer_checking:
                    checking_font = pygame.font.SysFont('arial', 30, bold=True)
                    checking_surf = checking_font.render('Checking answer...', True, (180, 180, 220))
                    screen.blit(checking_surf, (WIDTH//2 - checking_surf.get_width()//2, rect_y + rect_h + 20))
                elif self.show_entity_decision:
                    # Show Correct or Wrong answer with the actual feedback
                    result_font = pygame.font.SysFont('arial', 54, bold=True)
                    if self.question_feedback.startswith('Correct'):
                        result_text = 'Correct!'
                        color = (80, 220, 120)
                        # For correct answers, render normally since it's short
                        rsurf = result_font.render(result_text, True, color)
                        screen.blit(rsurf, (WIDTH//2 - rsurf.get_width()//2, rect_y + rect_h + 40))
                    else:
                        # Use the actual feedback which contains the correct answer
                        result_text = self.question_feedback
                        color = (255, 99, 71)
                        # Wrap the long answer text to fit screen width
                        result_lines = wrap_text(result_text, result_font, WIDTH - 100)  # Leave 50px margin on each side
                        for i, line in enumerate(result_lines):
                            rsurf = result_font.render(line.strip(), True, color)
                            screen.blit(rsurf, (WIDTH//2 - rsurf.get_width()//2, rect_y + rect_h + 40 + i*60))
                elif self.question_feedback:
                    color = (80, 220, 120) if self.question_feedback.startswith('Correct') else (255, 99, 71)
                    fsurf = font.render(self.question_feedback, True, color)
                    screen.blit(fsurf, (WIDTH//2 - fsurf.get_width()//2, rect_y + rect_h + 20))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and not self.answer_checking and not self.show_entity_decision:
                        if event.key == pygame.K_BACKSPACE:
                            self.user_text = self.user_text[:-1]
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            self.answer_checking = True
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                        else:
                            if len(self.user_text) < 60 and event.unicode.isprintable():
                                self.user_text += event.unicode
                # If answer_checking, do the answer check (AI disabled for demo)
                if self.answer_checking and self.ai_result is None:
                    if self.is_math_question:
                        is_correct, ai_msg = self.check_math_answer(self.question_data['question'], self.question_data['answer'], self.user_text)
                    else:
                        # Use local case-insensitive check for JSON questions (AI disabled for demo)
                        print(f"[INFO] Using local case-insensitive check for JSON question")
                        is_correct, ai_msg = self.check_json_answer_locally(self.question_data['question'], self.question_data['answer'], self.user_text)
                    if is_correct:
                        self.question_feedback = 'Correct!'
                    else:
                        self.question_feedback = f"Wrong! {ai_msg.strip()}"
                    self.answer_checking = False
                    self.show_entity_decision = True
                    self.entity_decision_time = time.time()
                    self.ai_result = (is_correct, ai_msg)
                # Show entity decision for 3 seconds before continuing
                if self.show_entity_decision:
                    if time.time() - self.entity_decision_time >= 3.0:
                        self.show_entity_decision = False
                        self.question_mode = False
                        self.next_question_time = time.time() + random.choice(MATH_INTERVALS)
                        self.question_feedback = ''
                        self.question_feedback_timer = 0
                    continue
                continue
            if self.story_mode:
                screen.fill((30, 30, 40))
                # Draw player and entity images
                screen.blit(self.player_img, (80, HEIGHT//2 - 110))
                blit_rounded(screen, self.entity_img, (WIDTH - 300, HEIGHT//2 - 150), radius=15)
                # Draw dialogue box
                pygame.draw.rect(screen, (40, 40, 60), (200, HEIGHT - 220, WIDTH - 400, 160), border_radius=20)
                pygame.draw.rect(screen, (100, 100, 160), (200, HEIGHT - 220, WIDTH - 400, 160), 4, border_radius=20)
                # Show dialogue or choice
                if self.story_index < len(self.story_dialogue):
                    who, text = self.story_dialogue[self.story_index]
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
                    yes_color = (255,255,0) if self.choice_selected == 0 else (200,200,200)
                    no_color = (255,255,0) if self.choice_selected == 1 else (200,200,200)
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
                        if self.story_index < len(self.story_dialogue):
                            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                                self.story_index += 1
                        else:
                            if event.key in (pygame.K_LEFT, pygame.K_a):
                                self.choice_selected = 0
                            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                                self.choice_selected = 1
                            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                                self.story_choice = 'yes' if self.choice_selected == 0 else 'no'
                                self.story_mode = False
                                # If 'no', show evil laugh for a moment before starting game
                                if self.story_choice == 'no':
                                    laugh_font = pygame.font.SysFont('arial', 60, bold=True)
                                    laugh_text = laugh_font.render('Wrong choice, Hahahahahahah', True, (255, 99, 71))
                                    screen.fill((30, 30, 40))
                                    blit_rounded(screen, self.entity_img, (WIDTH//2 - 110, HEIGHT//2 - 150), radius=15)
                                    screen.blit(laugh_text, (WIDTH//2 - laugh_text.get_width()//2, HEIGHT - 200))
                                    pygame.display.flip()
                                    pygame.time.delay(1800)
                                # Set obstacle frequency
                                self.spawn_interval = SPAWN_INTERVAL_FAST if self.story_choice == 'no' else SPAWN_INTERVAL_SLOW
                continue
            screen.fill((30, 30, 40))
            # Draw parallax background
            for i, layer in enumerate(BG_LAYERS):
                speed = layer['speed']
                self.bg_offsets[i] = (self.bg_offsets[i] - speed) % WIDTH
                x1 = int(self.bg_offsets[i])
                x2 = x1 - WIDTH
                screen.blit(self.bg_images[i], (x1, 0))
                screen.blit(self.bg_images[i], (x2, 0))
            # Show warning 5 seconds before entity appears
            if not self.story_mode and not self.question_mode and not self.game_over:
                time_to_entity = self.next_question_time - self.now
                if 0 < time_to_entity <= 5:
                    warn_font = pygame.font.SysFont('arial', 36, bold=True)
                    warn_text = warn_font.render('Warning: The Entity will appear soon!', True, (255, 99, 71))
                    screen.blit(warn_text, (WIDTH//2 - warn_text.get_width()//2, 20))
            # Ball horizontal movement
            if not self.game_over:
                self.ball_x += BALL_SPEED
                if self.ball_x > ANCHOR_X:
                    # Keep the ball at anchor, move obstacles left instead
                    shift = self.ball_x - ANCHOR_X
                    self.ball_x = ANCHOR_X
                    obstacles = [(ox - shift, olane, frame_idx) for ox, olane, frame_idx in self.obstacles]
                    pickables = [(px - shift, plane, anim_index, anim_timer) for (px, plane, anim_index, anim_timer) in self.pickables]
                    powerups = [(ppx - shift, pplane, ptype, *pdata) for (ppx, pplane, ptype, *pdata) in self.powerups]
            # Draw platforms as lines
            pygame.draw.line(screen, (80, 80, 120), (0, PLATFORM_Y_TOP), (WIDTH, PLATFORM_Y_TOP), PLATFORM_THICKNESS)
            pygame.draw.line(screen, (80, 80, 120), (0, PLATFORM_Y_BOTTOM), (WIDTH, PLATFORM_Y_BOTTOM), PLATFORM_THICKNESS)
            # Ball glide logic
            if self.ball_glide > 0:
                start_y = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2 if self.ball_lane == 0 else PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
                end_y = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2 if self.target_lane == 0 else PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
                t = (GLIDE_FRAMES - self.ball_glide + 1) / GLIDE_FRAMES
                self.ball_y = int(start_y + (end_y - start_y) * t)
                self.ball_glide -= 1
                if self.ball_glide == 0:
                    self.ball_lane = self.target_lane
                    self.ball_y = end_y
                    self.character_flipped = not self.character_flipped  # Flip character on switch
            else:
                self.ball_y = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2 if self.ball_lane == 0 else PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
            # Draw character run/hurt/death animation instead of ball
            if self.character_visible:
                # Draw invincibility bubble if active
                if self.invincible:
                    blit_transparent_bubble(screen, self.bubble_img, (int(self.ball_x), self.ball_y), scale=2.2, alpha=140)
                if self.death_anim_playing:
                    if self.death_anim_index < DEATH_FRAMES:
                        self.death_anim_timer += 1
                        if self.death_anim_timer >= DEATH_ANIM_SPEED:
                            self.death_anim_index += 1
                            self.death_anim_timer = 0
                        if self.death_anim_index < DEATH_FRAMES:
                            frame = self.death_frames[self.death_anim_index]
                            frame_scaled = pygame.transform.scale(frame, (BALL_RADIUS * 2, BALL_RADIUS * 2))
                            if self.character_flipped:
                                frame_scaled = pygame.transform.flip(frame_scaled, False, True)
                            screen.blit(frame_scaled, (int(self.ball_x) - BALL_RADIUS, self.ball_y - BALL_RADIUS))
                    if self.death_anim_index >= DEATH_FRAMES:
                        self.character_visible = False
                        self.death_anim_playing = False
                elif self.is_hurt:
                    self.hurt_anim_timer += 1
                    if self.hurt_anim_timer >= HURT_ANIM_SPEED:
                        self.hurt_anim_index += 1
                        self.hurt_anim_timer = 0
                        if self.hurt_anim_index >= HURT_FRAMES:
                            self.is_hurt = False
                            self.hurt_anim_index = 0
                    if self.hurt_anim_index < HURT_FRAMES:
                        frame = self.hurt_frames[self.hurt_anim_index]
                        frame_scaled = pygame.transform.scale(frame, (BALL_RADIUS * 2, BALL_RADIUS * 2))
                        if self.character_flipped:
                            frame_scaled = pygame.transform.flip(frame_scaled, False, True)
                        screen.blit(frame_scaled, (int(self.ball_x) - BALL_RADIUS, self.ball_y - BALL_RADIUS))
                else:
                    self.character_anim_timer += 1
                    if self.character_anim_timer >= CHARACTER_ANIM_SPEED:
                        self.character_anim_index = (self.character_anim_index + 1) % CHARACTER_FRAMES
                        self.character_anim_timer = 0
                    frame = self.character_frames[self.character_anim_index]
                    frame_scaled = pygame.transform.scale(frame, (BALL_RADIUS * 2, BALL_RADIUS * 2))
                    if self.character_flipped:
                        frame_scaled = pygame.transform.flip(frame_scaled, False, True)  # Vertical flip
                    screen.blit(frame_scaled, (int(self.ball_x) - BALL_RADIUS, self.ball_y - BALL_RADIUS))
            # (Removed ball spin effect)
            # Draw and animate pickables
            for idx, (px, plane, anim_index, anim_timer) in enumerate(self.pickables):
                if plane == 0:
                    py = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2
                else:
                    py = PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
                # Draw current frame
                frame = self.xp_coin_images[anim_index]
                screen.blit(frame, (int(px) - PICKABLE_RADIUS, py - PICKABLE_RADIUS))
                # Animate
                anim_timer += 1
                if anim_timer >= PICKABLE_ANIM_SPEED:
                    anim_index = (anim_index + 1) % XP_COIN_FRAMES
                    anim_timer = 0
                self.pickables[idx] = (px, plane, anim_index, anim_timer)
            # Draw powerups
            for ppx, pplane, ptype, *pdata in self.powerups:
                if pplane == 0:
                    ppy = PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2
                else:
                    ppy = PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2
                if ptype == POWERUP_TYPE_INVINCIBLE:
                    screen.blit(self.bubble_img, (int(ppx) - POWERUP_RADIUS, ppy - POWERUP_RADIUS))
                elif ptype == POWERUP_TYPE_HEART:
                    screen.blit(self.life_img, (int(ppx) - POWERUP_RADIUS, ppy - POWERUP_RADIUS))
            # Draw obstacles
            for ox, olane, frame_idx in self.obstacles:
                if olane == 0:
                    oy = PLATFORM_Y_TOP + PLATFORM_THICKNESS // 2
                    spike_img = pygame.transform.scale(self.spikes_frames[frame_idx], (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
                    spike_img = pygame.transform.flip(spike_img, False, True)  # Flip vertically for top lane
                else:
                    oy = PLATFORM_Y_BOTTOM - OBSTACLE_HEIGHT - PLATFORM_THICKNESS // 2
                    spike_img = pygame.transform.scale(self.spikes_frames[frame_idx], (OBSTACLE_WIDTH, OBSTACLE_HEIGHT))
                screen.blit(spike_img, (ox, oy))
            # Draw lives
            for i in range(self.lives):
                x = WIDTH - 80 - i * 64
                y = 80
                if self.invincible:
                    # Optionally tint or animate if invincible
                    screen.blit(self.life_img, (x - 30, y - 30))
                else:
                    screen.blit(self.life_img, (x - 30, y - 30))
            # Game over
            if self.game_over:
                # If death animation is playing, wait for it to finish
                if self.death_anim_playing:
                    pygame.display.flip()
                    continue
                # If character is not visible (death animation finished), show Game Over
                if not self.character_visible:
                    over_text = font.render('Game Over!', True, (255,255,255))
                    screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 30))
                    pygame.display.flip()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                    continue
            # Draw XP
            xp_surf = font.render(f'XP: {self.xp}', True, (255, 255, 100))
            screen.blit(xp_surf, (40, 40))
            # Move obstacles
            self.obstacles = [(ox - self.obstacle_speed, olane, frame_idx) for ox, olane, frame_idx in self.obstacles if ox > -OBSTACLE_WIDTH]
            self.pickables = [(px - self.obstacle_speed, plane, anim_index, anim_timer) for (px, plane, anim_index, anim_timer) in self.pickables if px > -PICKABLE_RADIUS]
            self.powerups = [(ppx - self.obstacle_speed, pplane, ptype, *pdata) for (ppx, pplane, ptype, *pdata) in self.powerups if ppx > -POWERUP_RADIUS]
            # Spawn new obstacles
            self.frame_count += 1
            if self.frame_count % self.spawn_interval == 0:
                lane = random.randint(0, 1)
                frame_idx = random.randint(0, SPIKES_FRAMES - 1)
                self.obstacles.append((WIDTH, lane, frame_idx))
            # Spawn new pickables
            if self.frame_count % PICKABLE_SPAWN_INTERVAL == 0:
                lane = random.randint(0, 1)
                # Check for overlap with obstacles in the same lane
                overlap = False
                for ox, olane, frame_idx in self.obstacles:
                    if olane == lane and abs(ox - WIDTH) < OBSTACLE_WIDTH + PICKABLE_RADIUS * 2:
                        overlap = True
                        break
                if not overlap:
                    # Start each pickable at a random frame for independent animation
                    self.pickables.append((WIDTH, lane, random.randint(0, XP_COIN_FRAMES-1), 0))
            # Collision detection (only when not gliding)
            if self.ball_glide == 0:
                for ox, olane, frame_idx in self.obstacles:
                    if self.invincible:
                        continue
                    if olane == self.ball_lane:
                        if olane == 0:
                            ball_center = (int(self.ball_x), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                            obs_rect = pygame.Rect(ox, PLATFORM_Y_TOP + PLATFORM_THICKNESS // 2, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                        else:
                            ball_center = (int(self.ball_x), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                            obs_rect = pygame.Rect(ox, PLATFORM_Y_BOTTOM - OBSTACLE_HEIGHT - PLATFORM_THICKNESS // 2, OBSTACLE_WIDTH, OBSTACLE_HEIGHT)
                        cx, cy = ball_center
                        rx, ry, rw, rh = obs_rect
                        closest_x = max(rx, min(cx, rx + rw))
                        closest_y = max(ry, min(cy, ry + rh))
                        dist = ((cx - closest_x) ** 2 + (cy - closest_y) ** 2) ** 0.5
                        if dist < BALL_RADIUS:
                            if not self.is_hurt and not self.death_anim_playing:
                                if self.lives > 1:
                                    self.is_hurt = True
                                    self.hurt_anim_index = 0
                                    self.hurt_anim_timer = 0
                                self.lives -= 1
                                self.obstacles.remove((ox, olane, frame_idx))
                                if self.lives <= 0:
                                    self.death_anim_playing = True
                                    self.death_anim_index = 0
                                    self.death_anim_timer = 0
                                    self.game_over = True
                                break
                # Pickable collision
                for pick in self.pickables[:]:
                    px, plane, anim_index, anim_timer = pick
                    if plane == self.ball_lane:
                        if plane == 0:
                            ball_center = (int(self.ball_x), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                            pick_center = (int(px), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                        else:
                            ball_center = (int(self.ball_x), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                            pick_center = (int(px), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                        dist = ((ball_center[0] - pick_center[0]) ** 2 + (ball_center[1] - pick_center[1]) ** 2) ** 0.5
                        if dist < BALL_RADIUS + PICKABLE_RADIUS:
                            self.xp += 15
                            self.pickables.remove(pick)
                # Powerup collision
                for powerup in self.powerups[:]:
                    ppx, pplane, ptype, *pdata = powerup
                    if pplane == self.ball_lane:
                        if pplane == 0:
                            ball_center = (int(self.ball_x), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                            powerup_center = (int(ppx), PLATFORM_Y_TOP + BALL_RADIUS + PLATFORM_THICKNESS // 2)
                        else:
                            ball_center = (int(self.ball_x), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                            powerup_center = (int(ppx), PLATFORM_Y_BOTTOM - BALL_RADIUS - PLATFORM_THICKNESS // 2)
                        dist = ((ball_center[0] - powerup_center[0]) ** 2 + (ball_center[1] - powerup_center[1]) ** 2) ** 0.5
                        if dist < BALL_RADIUS + POWERUP_RADIUS:
                            if ptype == POWERUP_TYPE_INVINCIBLE:
                                duration = pdata[0] if pdata else 7
                                self.invincible = True
                                self.invincible_timer = time.time() + duration
                            elif ptype == POWERUP_TYPE_HEART:
                                self.lives = min(self.lives + 1, 9)
                            self.powerups.remove(powerup)
            # Input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE and self.ball_glide == 0:
                        self.target_lane = 1 - self.ball_lane
                        self.ball_glide = GLIDE_FRAMES
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and self.ball_glide == 0:
                    self.target_lane = 1 - self.ball_lane
                    self.ball_glide = GLIDE_FRAMES
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    import pygame
    print("[DEBUG] Starting SwitchRunnerGame main block")
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Switch Runner')
    game = SwitchRunnerGame()
    game.run(screen)
