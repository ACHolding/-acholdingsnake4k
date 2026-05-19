import pygame
import random
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Setup display (Change this to any size, everything adapts!)
WINDOW_SIZE = 600
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("60 FPS Dynamic Snake Game")

# Clock to control 60 FPS
clock = pygame.time.Clock()
FPS = 60

# Game Constants
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Colors
COLOR_BG = (15, 15, 25)
COLOR_SNAKE = (0, 255, 150)
COLOR_APPLE = (255, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_MUTED = (100, 100, 120)
COLOR_SELECT = (255, 215, 0) # Gold highlight for selected option

# --- Procedural Beeps 'n' Boops ---
def generate_sound(frequency, duration_ms):
    """Generates a simple square wave sound purely in memory."""
    sample_rate = 22050
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    buffer = bytearray()
    
    period = sample_rate / frequency
    for i in range(num_samples):
        if (i % period) < (period / 2):
            buffer.append(127)
        else:
            buffer.append(0)
            
    sound = pygame.mixer.Sound(buffer=buffer)
    sound.set_volume(0.2)
    return sound

# Generate retro SFX
sound_eat = generate_sound(880, 80)     
sound_fail = generate_sound(220, 300)   
sound_menu = generate_sound(440, 50) # Small blip for menu navigation

# Game States
STATE_MENU = "MENU"
STATE_GAME = "GAME"
current_state = STATE_MENU

# Menu Selection State
menu_options = ["PLAY GAME", "EXIT"]
menu_index = 0

# Game State Variables
snake = []
direction = (0, -1)
apple = (0, 0)
score = 0
move_delay = 6  
frame_counter = 0

def reset_game():
    global snake, direction, apple, score, frame_counter, GRID_COUNT
    GRID_COUNT = WINDOW_SIZE // GRID_SIZE # Recalculate if window size changed
    snake = [(GRID_COUNT // 2, GRID_COUNT // 2), (GRID_COUNT // 2, GRID_COUNT // 2 + 1), (GRID_COUNT // 2, GRID_COUNT // 2 + 2)]
    direction = (0, -1)
    apple = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
    score = 0
    frame_counter = 0

# --- Dynamic Font Sizing based on Window Size ---
# Scales font size smoothly according to the screen width
font_large = pygame.font.SysFont("monospace", int(WINDOW_SIZE * 0.04), bold=True)
font_medium = pygame.font.SysFont("monospace", int(WINDOW_SIZE * 0.04))
font_small = pygame.font.SysFont("monospace", int(WINDOW_SIZE * 0.025))

# Main Game Loop
while True:
    
    # ==========================
    # 1. MAIN MENU STATE
    # ==========================
    if current_state == STATE_MENU:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    sound_menu.play()
                    menu_index = (menu_index - 1) % len(menu_options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    sound_menu.play()
                    menu_index = (menu_index + 1) % len(menu_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if menu_options[menu_index] == "PLAY GAME":
                        reset_game()
                        current_state = STATE_GAME
                    elif menu_options[menu_index] == "EXIT":
                        pygame.quit()
                        sys.exit()

        # Render Menu Graphics
        screen.fill(COLOR_BG)
        
        # 1. Dynamic Logo Position (Centered vertically at 35% of screen height)
        logo_text = "ac's snake engine v infdev 0.1 beta"
        logo_surface = font_large.render(logo_text, True, COLOR_SNAKE)
        logo_rect = logo_surface.get_rect(center=(WINDOW_SIZE // 2, int(WINDOW_SIZE * 0.35)))
        screen.blit(logo_surface, logo_rect)
        
        # 2. Dynamic Menu Options Position (Centered vertically starting at 55% height)
        for idx, option in enumerate(menu_options):
            if idx == menu_index:
                text_color = COLOR_SELECT
                display_text = f"> {option} <"
            else:
                text_color = COLOR_TEXT
                display_text = option
                
            option_surface = font_medium.render(display_text, True, text_color)
            
            # Spacing between options scales based on window height
            row_y = int(WINDOW_SIZE * 0.55) + (idx * int(WINDOW_SIZE * 0.08))
            option_rect = option_surface.get_rect(center=(WINDOW_SIZE // 2, row_y))
            screen.blit(option_surface, option_rect)

        # 3. Dynamic Control Hint Position (Fixed at 7% from the bottom of the screen)
        hint_surface = font_small.render("Use UP/DOWN Arrows & Press ENTER to select", True, COLOR_MUTED)
        hint_rect = hint_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE - int(WINDOW_SIZE * 0.07)))
        screen.blit(hint_surface, hint_rect)

    # ==========================
    # 2. GAMEPLAY STATE
    # ==========================
    elif current_state == STATE_GAME:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == pygame.K_r:  # Manual return to menu
                    current_state = STATE_MENU

        # Game Logic Updates
        frame_counter += 1
        if frame_counter >= move_delay:
            frame_counter = 0
            
            head_x, head_y = snake[0]
            dir_x, dir_y = direction
            new_head = (head_x + dir_x, head_y + dir_y)

            # Collision detection: Return to menu on death
            if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or 
                new_head[1] < 0 or new_head[1] >= GRID_COUNT or 
                new_head in snake):
                sound_fail.play()
                pygame.time.wait(1000)
                current_state = STATE_MENU
                continue

            snake.insert(0, new_head)

            if new_head == apple:
                score += 1
                sound_eat.play()
                while True:
                    apple = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
                    if apple not in snake:
                        break
            else:
                snake.pop()

        # Render Gameplay Graphics
        screen.fill(COLOR_BG)

        # Draw Apple
        apple_rect = pygame.Rect(apple[0] * GRID_SIZE, apple[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
        pygame.draw.rect(screen, COLOR_APPLE, apple_rect)

        # Draw Snake
        for segment in snake:
            snake_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.rect(screen, COLOR_SNAKE, snake_rect)

        # 4. Dynamic Score Board (Offset dynamically from the top-left corner)
        score_text = font_medium.render(f"SCORE: {score}", True, COLOR_TEXT)
        offset_pos = int(WINDOW_SIZE * 0.025)
        screen.blit(score_text, (offset_pos, offset_pos))

    # Update screen and tick clock
    pygame.display.flip()
    clock.tick(FPS)
