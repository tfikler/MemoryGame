import pygame
import random
import time

# Initialize Pygame and font module
pygame.init()
pygame.font.init()  # Initialize the font module

# Screen dimensions and title
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Game")

# Colors
BACKGROUND_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BUTTON_COLOR = (0, 255, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
colors = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
    (255, 100, 255), (100, 255, 255), (255, 140, 0), (140, 70, 20)
]

# Game variables
tile_width = SCREEN_WIDTH // 5 - 40
tile_height = (SCREEN_HEIGHT // 5) - 40
tile_margin = 20
tiles = []  # (color, matched)
selected_tiles = []
matching_tiles = []

# Initialize tiles
for color in colors * 2:  # Duplicate each color to create pairs
    tiles.append((color, False))  # False indicates unmatched
random.shuffle(tiles)

# Timer and Font setup
font = pygame.font.SysFont(None, 40)  # Create a font object
start_time = time.time()  # Record the start time

# Quit button setup
button_font = pygame.font.SysFont(None, 30)
quit_button = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60, 120, 40)

# Reset button setup
reset_button = pygame.Rect(SCREEN_WIDTH - 300, SCREEN_HEIGHT - 60, 120, 40)


def draw_tiles():
    screen.fill(BACKGROUND_COLOR)
    for i, (color, matched) in enumerate(tiles):
        row = i // 4
        col = i % 4
        x = col * (tile_width + tile_margin) + tile_margin
        y = row * (tile_height + tile_margin) + tile_margin + 40  # Adjust y to leave space for the timer

        if i in selected_tiles or matched:
            pygame.draw.rect(screen, color, (x, y, tile_width, tile_height))
        else:
            pygame.draw.rect(screen, GRAY, (x, y, tile_width, tile_height))

        # Draw border for aesthetic purposes
        pygame.draw.rect(screen, WHITE, (x, y, tile_width, tile_height), 3)

    # Display the timer
    elapsed_time = time.time() - start_time
    minutes = int(elapsed_time // 60)
    seconds = int(elapsed_time % 60)
    timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
    screen.blit(timer_text, (SCREEN_WIDTH - 100, 10))

    # Draw quit button
    pygame.draw.rect(screen, BUTTON_COLOR, quit_button)  # Quit button
    quit_text = button_font.render('Quit', True, BUTTON_TEXT_COLOR)
    screen.blit(quit_text, (quit_button.x + 35, quit_button.y + 10))

    # Drawing the reset button in draw_tiles() function or wherever you draw your screen elements
    pygame.draw.rect(screen, BUTTON_COLOR, reset_button)  # Reset button
    reset_text = button_font.render('Reset', True, BUTTON_TEXT_COLOR)
    screen.blit(reset_text, (reset_button.x + 30, reset_button.y + 10))

    pygame.display.flip()


def reveal_tiles(index):
    if tiles[index][1] == False and index not in selected_tiles:
        selected_tiles.append(index)


def check_match():
    global tiles, selected_tiles
    if len(selected_tiles) == 2:
        idx1, idx2 = selected_tiles
        if tiles[idx1][0] == tiles[idx2][0]:
            tiles[idx1] = (tiles[idx1][0], True)
            tiles[idx2] = (tiles[idx2][0], True)
            matching_tiles.extend([idx1, idx2])
            play_match_correct_sound()
        else:
            # Reveal the second selected tile before hiding both
            play_not_match_sound()
            draw_tiles()
            pygame.time.wait(1000)  # Delay to show cards
        selected_tiles.clear()


def check_quit_button(x, y):
    if quit_button.collidepoint(x, y):
        pygame.quit()
        exit()


def play_match_correct_sound():
    pygame.mixer.music.load('match_sound.mp3')
    pygame.mixer.music.play()


def play_not_match_sound():
    pygame.mixer.music.load('not_match_sound.mp3')
    pygame.mixer.music.play()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if reset_button.collidepoint(x, y):
                tiles = []
                for color in colors * 2:
                    tiles.append((color, False))
                random.shuffle(tiles)
                selected_tiles.clear()
                matching_tiles.clear()
                start_time = time.time()
                draw_tiles()
            check_quit_button(x, y)  # Check if quit button was pressed
            if not quit_button.collidepoint(x, y):  # Proceed if Quit button wasn't clicked
                col = x // (tile_width + tile_margin)
                row = (y - 40) // (tile_height + tile_margin)  # Adjust for the added y offset
                index = row * 4 + col
                if 0 <= index < len(tiles):
                    reveal_tiles(index)
                    if len(selected_tiles) == 2:
                        check_match()

        draw_tiles()

pygame.quit()

