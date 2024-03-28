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
# start_time = time.time()  # Record the start time

# Quit button setup
button_font = pygame.font.SysFont(None, 30)
quit_button = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60, 120, 40)

# Reset button setup
reset_button = pygame.Rect(SCREEN_WIDTH - 300, SCREEN_HEIGHT - 60, 120, 40)

# Play again button setup
play_again_button = pygame.Rect(SCREEN_WIDTH - 300, SCREEN_HEIGHT - 50, 150, 40)

# Player selection buttons setup
one_player_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50)
two_player_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)

pairs_found = 0

# Initialize scores and timers
player_scores = [0, 0]  # Player 1 and Player 2 scores
player_timers = [0, 0]  # Player 1 and Player 2 timers

start_time = [time.time(), 0]  # Start time for Player 1, Player 2 doesn't start until it's their turn
current_player = 1  # Start with Player 1


def reset_timers():
    global start_time
    start_time = [time.time(), 0]
    update_timers()


def update_timers():
    global player_timers
    # Update only the current player's timer
    elapsed_time = time.time() - start_time[current_player - 1]
    player_timers[current_player - 1] += elapsed_time
    # Reset start time for the current player
    start_time[current_player - 1] = time.time()


def draw_scoreboard():
    padding = 10  # Padding inside the scoreboard
    line_spacing = 5  # Space between lines

    for i in range(num_players):
        base_x = 20 + (SCREEN_WIDTH / 3) * i  # Adjust base X for better spacing
        text_y = SCREEN_HEIGHT - 100  # Position scoreboard higher

        # Player Text
        player_text = font.render(f"Player {i + 1}:", True, WHITE)
        screen.blit(player_text, (base_x, text_y))

        # Score Text
        score_text_y = text_y + player_text.get_height() + line_spacing
        score_text = font.render(f"Score: {player_scores[i]}", True, WHITE)
        screen.blit(score_text, (base_x, score_text_y))

        # Timer Text
        timer_text_y = score_text_y + score_text.get_height() + line_spacing
        minutes, seconds = divmod(int(player_timers[i]), 60)
        timer_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(timer_text, (base_x, timer_text_y))


def draw_player_selection():
    screen.fill(BACKGROUND_COLOR)
    one_player_text = font.render('1 Player', True, WHITE)
    two_player_text = font.render('2 Players', True, WHITE)
    pygame.draw.rect(screen, BUTTON_COLOR, one_player_button)
    pygame.draw.rect(screen, BUTTON_COLOR, two_player_button)
    screen.blit(one_player_text, (one_player_button.x + 10, one_player_button.y + 10))
    screen.blit(two_player_text, (two_player_button.x + 10, two_player_button.y + 10))
    pygame.display.flip()

    selecting = True
    while selecting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                print(True)
                x, y = pygame.mouse.get_pos()
                if one_player_button.collidepoint(x, y):
                    return 1
                elif two_player_button.collidepoint(x, y):
                    return 2


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

        if num_players == 2:
            player_text = font.render(f'Player {current_player}', True, WHITE)
            screen.blit(player_text, (10, 10))

        # Draw border for aesthetic purposes
        pygame.draw.rect(screen, WHITE, (x, y, tile_width, tile_height), 3)

    # Display the timer
    # elapsed_time = time.time() - start_time
    # minutes = int(elapsed_time // 60)
    # seconds = int(elapsed_time % 60)
    # timer_text = font.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
    # screen.blit(timer_text, (SCREEN_WIDTH - 100, 10))

    # Draw quit button
    pygame.draw.rect(screen, BUTTON_COLOR, quit_button)  # Quit button
    quit_text = button_font.render('Quit', True, BUTTON_TEXT_COLOR)
    screen.blit(quit_text, (quit_button.x + 35, quit_button.y + 10))

    # Drawing the reset button in draw_tiles() function or wherever you draw your screen elements
    pygame.draw.rect(screen, BUTTON_COLOR, reset_button)  # Reset button
    reset_text = button_font.render('Reset', True, BUTTON_TEXT_COLOR)
    screen.blit(reset_text, (reset_button.x + 30, reset_button.y + 10))

    # Draw the score board
    draw_scoreboard()
    pygame.display.flip()


def reveal_tiles(index):
    if tiles[index][1] == False and index not in selected_tiles:
        selected_tiles.append(index)


def check_match():
    global tiles, selected_tiles, pairs_found, current_player
    if len(selected_tiles) == 2:
        idx1, idx2 = selected_tiles
        if tiles[idx1][0] == tiles[idx2][0]:
            tiles[idx1] = (tiles[idx1][0], True)
            tiles[idx2] = (tiles[idx2][0], True)
            matching_tiles.extend([idx1, idx2])
            play_match_correct_sound()
            pairs_found += 1
            player_scores[current_player - 1] += 1
            if pairs_found == 4:
                handle_game_won()
        else:
            # Reveal the second selected tile before hiding both
            play_not_match_sound()
            draw_tiles()
            pygame.time.wait(1000)  # Delay to show cards
            if num_players == 2:
                current_player = 1 if current_player == 2 else 2
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


def handle_game_won():
    screen.fill(BACKGROUND_COLOR)
    text = font.render("Well done!!", True, WHITE)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    pygame.draw.rect(screen, BUTTON_COLOR, play_again_button)
    play_again_text = button_font.render('Play Again', True, BUTTON_TEXT_COLOR)
    screen.blit(play_again_text, (play_again_button.x + 20, play_again_button.y + 10))
    pygame.display.flip()

    # Wait for Play Again button click
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if reset_button.collidepoint(x, y):
                    waiting_for_input = False
                    # Reset the game state here
                    reset_game()


def reset_game():
    global tiles, selected_tiles, matching_tiles, start_time, player_timers, player_scores, current_player, pairs_found
    tiles = []
    for color in colors * 2:  # Duplicate each color to create pairs
        tiles.append((color, False))  # False indicates unmatched
    random.shuffle(tiles)
    selected_tiles = []
    matching_tiles = []
    pairs_found = 0
    start_time = [time.time(), 0]  # Reset start times for both players
    player_timers = [0, 0]  # Reset timers for both players
    player_scores = [0, 0]  # Reset scores for both players
    current_player = 1  # Reset to start with Player 1
    draw_tiles()


num_players = draw_player_selection()

running = True
while running:
    update_timers()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if reset_button.collidepoint(x, y):
                reset_game()
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

