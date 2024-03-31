import threading

import pygame
import random
import time
from voice_controller import start_listening, load_model, stop_listening
from word2number import w2n

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
background = pygame.image.load('img.png')
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BUTTON_COLOR = (143, 85, 45)
BORDER_COLOR = (249, 244, 229)
BUTTON_TEXT_COLOR = (232, 237, 238)
colors = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
    (255, 100, 255), (100, 255, 255), (255, 140, 0), (140, 70, 20)
]

# Image paths for wild mode
image_paths = ['assets/e^x_graph.png', 'assets/e^x.png', 'assets/sinx.png', 'assets/sinx_graph.png', 'assets/tanx.png', 'assets/tanx_graph.jpeg',
                   'assets/1overx.png', 'assets/1overx_graph.png', 'assets/lnx.png', 'assets/lnx_graph.png', 'assets/nd_graph.png', 'assets/nd.jpeg',
                   'assets/x^2.png', 'assets/x^2_graph.png', 'assets/absx.png', 'assets/absx_graph.png']

# Game variables
tile_width = SCREEN_WIDTH // 5 - 40
tile_height = (SCREEN_HEIGHT // 5) - 40
tile_margin = 20
tiles = []  # (color, matched)
selected_tiles = []
matching_tiles = []

# Initialize tiles
for color in colors * 2:  # Duplicate each color to create pairs
    tiles.append((color, False, None))  # False indicates unmatched
random.shuffle(tiles)

# Timer and Font setup
font = pygame.font.SysFont(None, 40)  # Create a font object
board_font = pygame.font.SysFont(None, 35)
# start_time = time.time()  # Record the start time

# Quit button setup
button_font = pygame.font.SysFont(None, 30)
quit_button = pygame.Rect(SCREEN_WIDTH - 125, SCREEN_HEIGHT - 45, 120, 40)

# Reset button setup
reset_button = pygame.Rect(SCREEN_WIDTH - 260, SCREEN_HEIGHT - 45, 120, 40)

# Play again button setup
play_again_button = pygame.Rect(SCREEN_WIDTH - 155, SCREEN_HEIGHT - 45, 150, 40)

# Player selection buttons setup
one_player_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 250, 200, 50)
two_player_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 175, 200, 50)

# Attack Mode button setup
attack_mode_button = pygame.Rect(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 250, 200, 50)

# Voice control mode button setup
voice_control_button = pygame.Rect(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2 - 250, 200, 50)
is_voice_control = False
user_text = []

# Wild mode button setup
wild_mode_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, 200, 50)
is_wild_mode = False

pairs_found = 0
first_turn = True
initial_attack_mode_time = 45
player_won = False

# initialize attack mode timer
attack_mode_timer = 0
is_attack_mode = False

# Initialize scores and timers
player_scores = [0, 0]  # Player 1 and Player 2 scores
player_timers = [0, 0]  # Player 1 and Player 2 timers

# start_time = [time.time(), time.time()]  # Start time for Player 1, Player 2 doesn't start until it's their turn
pause_time = [0.0, 0.0]  # Pause time for Player 1, Player 2 doesn't pause until it's their turn
current_player = 1  # Start with Player 1


def switch_player():
    global current_player, pause_time, start_time
    # Pause the current player's timer
    pause_timers()
    # Switch player
    current_player = 2 if current_player == 1 else 1
    # Reset the start time for the new current player to now, so their timer starts from now
    start_time[current_player - 1] = time.time()
    pause_time[current_player - 1] = 0  # Ensure the new current player's pause time is reset


def pause_timers():
    global pause_time, current_player
    pause_time[current_player - 1] = time.time()


def reset_timers():
    global start_time
    start_time = [time.time(), 0]
    update_timers()


def update_timers():
    global player_timers, start_time, pause_time
    # Calculate elapsed time only for the current player
    if pause_time[current_player - 1] != 0:
        # If the pause time is set, calculate the time before pausing
        elapsed_time = pause_time[current_player - 1] - start_time[current_player - 1]
        pause_time[current_player - 1] = 0  # Reset pause time
    else:
        # Otherwise, calculate the time normally
        elapsed_time = time.time() - start_time[current_player - 1]

    player_timers[current_player - 1] += elapsed_time
    start_time[current_player - 1] = time.time()  # Reset start time for the current player


def draw_scoreboard():
    global attack_mode_button, attack_mode_timer, tiles, first_turn, game_start_time
    padding = 10  # Padding inside the scoreboard
    line_spacing = 5  # Space between lines

    if is_attack_mode:
        # Display a warning message that the attack mode is active and user have 60 seconds to finish the game
        attack_mode_text = font.render(f'Attack Mode - You have {initial_attack_mode_time} seconds to finish the game', True, WHITE)
        screen.blit(attack_mode_text, (SCREEN_WIDTH // 2 - attack_mode_text.get_width() // 2, 10))

    if is_wild_mode:
        # Display a message that the wild mode is active and user have to find the function and its derivative
        wild_mode_text = font.render('Wild Mode - Find the function and its graph', True, WHITE)
        screen.blit(wild_mode_text, (SCREEN_WIDTH // 2 - wild_mode_text.get_width() // 2, 10))

    for i in range(num_players):
        base_x = 20 + (SCREEN_WIDTH / 3) * i * 0.75  # Adjust base X for better spacing
        text_y = SCREEN_HEIGHT - 90  # Position scoreboard higher

        # Player Text
        player_text = board_font.render(f"Player {i + 1}:", True, WHITE)
        screen.blit(player_text, (base_x, text_y))

        # Score Text
        score_text_y = text_y + player_text.get_height() + line_spacing
        score_text = board_font.render(f"Score: {player_scores[i]}", True, WHITE)
        screen.blit(score_text, (base_x, score_text_y))

        # Timer Text
        timer_text_y = score_text_y + score_text.get_height() + line_spacing
        minutes, seconds = divmod(int(player_timers[i]), 60)
        timer_text = board_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(timer_text, (base_x, timer_text_y))


def load_images(paths):
    images = []
    for path in paths:
        image = pygame.image.load(path)
        image_name = path.split('/')[-1]  # Extracts the filename from the path
        # Remove the '.png' or '.jpeg' extension and 'graph' word from the filename
        base_name = image_name.replace('.png', '').replace('.jpeg', '').replace('_graph', '')
        image = pygame.transform.scale(image, (tile_width, tile_height))  # Scale images to fit tiles
        images.append((image, False, base_name))
    return images


def draw_player_selection():
    global is_attack_mode, is_voice_control, is_wild_mode, game_start_time
    screen.blit(background, (0, 0))
    one_player_text = font.render('1 Player', True, WHITE)
    attack_mode_text = font.render('Attack Mode', True, WHITE)
    two_player_text = font.render('2 Players', True, WHITE)
    voice_control_text = font.render('Voice Control', True, WHITE)
    wild_mode_text = font.render('Wild Mode', True, WHITE)
    pygame.draw.rect(screen, BUTTON_COLOR, one_player_button)
    pygame.draw.rect(screen, BUTTON_COLOR, attack_mode_button)
    pygame.draw.rect(screen, BUTTON_COLOR, two_player_button)
    pygame.draw.rect(screen, BUTTON_COLOR, voice_control_button)
    pygame.draw.rect(screen, BUTTON_COLOR, wild_mode_button)
    screen.blit(one_player_text, (one_player_button.x + 40, one_player_button.y + 10))
    screen.blit(attack_mode_text, (attack_mode_button.x + 15, attack_mode_button.y + 10))
    screen.blit(two_player_text, (two_player_button.x + 40, two_player_button.y + 10))
    screen.blit(voice_control_text, (voice_control_button.x + 10, voice_control_button.y + 10))
    screen.blit(wild_mode_text, (wild_mode_button.x + 30, wild_mode_button.y + 10))
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
                if one_player_button.collidepoint(x, y) or attack_mode_button.collidepoint(x, y) or voice_control_button.collidepoint(x, y)\
                        or wild_mode_button.collidepoint(x, y):
                    if attack_mode_button.collidepoint(x, y):
                        is_attack_mode = True
                    if voice_control_button.collidepoint(x, y):
                        is_voice_control = True
                        load_model()
                    if wild_mode_button.collidepoint(x, y):
                        is_wild_mode = True
                    return 1
                elif two_player_button.collidepoint(x, y):
                    return 2


def draw_tiles():
    global is_voice_control
    screen.blit(background, (0, 0))
    for i, tile in enumerate(tiles):
        value, matched, pic_name = tile
        row = i // 4
        col = i % 4
        x = col * (tile_width + tile_margin) + tile_margin
        y = row * (tile_height + tile_margin) + tile_margin + 40  # Adjust y to leave space for the timer

        if i in selected_tiles or matched:
            if isinstance(value, pygame.Surface):
                screen.blit(value, (x, y))
            else:
                pygame.draw.rect(screen, value, (x, y, tile_width, tile_height))
        else:
            pygame.draw.rect(screen, GRAY, (x, y, tile_width, tile_height))

        # Draw the number of the tile
        if not matched and is_voice_control:
            tile_number = font.render(str(i + 1), True, WHITE)
            screen.blit(tile_number, (x + 10, y + 10))

        if num_players == 2:
            player_text = font.render(f'Player {current_player}', True, WHITE)
            screen.blit(player_text, (10, 10))

        # Draw border for aesthetic purposes
        pygame.draw.rect(screen, WHITE, (x, y, tile_width, tile_height), 3)

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
    global tiles, selected_tiles, is_wild_mode
    if tiles[index][1] == False and index not in selected_tiles:
        print(f"Revealing tile at index {index}")
        row = index // 4
        col = index % 4
        x = col * (tile_width + tile_margin) + tile_margin
        y = row * (tile_height + tile_margin) + tile_margin + 40  # Adjust y to leave space for the scoreboard

        # Phase 1: Shrink the tile to simulate flipping
        for width in range(tile_width, 0, -10):
            pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, tile_width, tile_height))  # Erase the old tile
            pygame.draw.rect(screen, GRAY, (x + (tile_width - width) // 2, y, width, tile_height))
            pygame.display.flip()
            pygame.time.wait(25)  # Control the speed of the animation

        # Phase 2: Expand the tile with the new color to simulate revealing
        for width in range(0, tile_width + 1, 10):
            new_color = tiles[index][0]  # The new color to reveal
            pygame.draw.rect(screen, BACKGROUND_COLOR, (x, y, tile_width, tile_height))  # Erase the old tile
            if isinstance(new_color, pygame.Surface):
                temp_surface = pygame.transform.scale(new_color, (width, tile_height))
                screen.blit(temp_surface, (x + (tile_width - width) // 2, y))
            else:
                pygame.draw.rect(screen, new_color, (x + (tile_width - width) // 2, y, width, tile_height))
            pygame.display.flip()
            pygame.time.wait(25)  # Control the speed of the animation

        selected_tiles.append(index)  # Add to selected tiles to reveal


def update_if_match(idx1, idx2):
    global pairs_found, player_scores, current_player, player_won
    matching_tiles.extend([idx1, idx2])
    play_match_correct_sound()
    pairs_found += 1
    player_scores[current_player - 1] += 1
    if pairs_found == len(tiles) // 2:
        player_won = True
        handle_game_won()


def check_match():
    global tiles, selected_tiles, pairs_found, current_player
    if len(selected_tiles) == 2:
        idx1, idx2 = selected_tiles
        if tiles[idx1][2] == tiles[idx2][2] and is_wild_mode:
            tiles[idx1] = (tiles[idx1][0], True, tiles[idx1][2])
            tiles[idx2] = (tiles[idx2][0], True, tiles[idx2][2])
            update_if_match(idx1, idx2)
        elif tiles[idx1][0] == tiles[idx2][0]:
            tiles[idx1] = (tiles[idx1][0], True, None)
            tiles[idx2] = (tiles[idx2][0], True, None)
            update_if_match(idx1, idx2)
        else:
            # Reveal the second selected tile before hiding both
            play_not_match_sound()
            draw_tiles()
            pygame.time.wait(400)  # Delay to show cards
            if num_players == 2:
                switch_player()
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
    if num_players == 1:
        handle_single_player_game_won()
    else:
        handle_two_player_game_won()


def won_menu():
    global is_attack_mode, initial_attack_mode_time, player_won
    if not is_attack_mode or not player_won:
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
                    if play_again_button.collidepoint(x, y):
                        waiting_for_input = False
                        # Reset timers
                        reset_timers()
                        # Reset the game state here
                        reset_game()
    elif is_attack_mode and player_won:
        initial_attack_mode_time -= 15
        new_attack_mode_game()
    elif is_attack_mode and not player_won:
        handle_game_lost_attack_mode()


def new_attack_mode_game():
    global tiles, selected_tiles, matching_tiles, start_time, player_timers, player_scores, current_player, pairs_found, game_start_time, player_won
    tiles = []
    for color in colors * 2:  # Duplicate each color to create pairs
        tiles.append((color, False, None))  # False indicates unmatched
    random.shuffle(tiles)
    selected_tiles = []
    matching_tiles = []
    pairs_found = 0
    start_time = [time.time(), 0]  # Reset start times for both players
    player_timers = [0, 0]  # Reset timers for both players
    player_scores = [0, 0]  # Reset scores for both players
    current_player = 1  # Reset to start with Player 1
    draw_tiles()
    player_won = False
    game_start_time = time.time()


def handle_single_player_game_won():
    screen.blit(background, (0,0))
    text = font.render("Well done!!", True, GRAY)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    won_menu()


def handle_two_player_game_won():
    won_player = 1 if player_scores[0] > player_scores[1] else 2
    if player_scores[0] == player_scores[1]:
        screen.blit(background, (0,0))
        text = font.render("It's a tie!!", True, GRAY)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        won_menu()
    else:
        screen.blit(background, (0,0))
        text = font.render(f"Player {won_player} wins!!", True, GRAY)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        won_menu()


def handle_game_lost_attack_mode():
    global player_won
    player_won = False
    print("Game lost!")
    screen.blit(background, (0,0))
    text = font.render("You lost!!", True, GRAY)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
    print("Attack mode time is up! - before showing menu")
    won_menu()


def voice_control_main_loop():
    global user_text
    if user_text:
        parsed_result = user_text.pop(0)
        if parsed_result == 'reset':
            reset_game()
        elif parsed_result == 'quit':
            pygame.quit()
            exit()
        else:
            try:
                index = int(w2n.word_to_num(parsed_result)) - 1
                if 0 <= index < len(tiles):
                    reveal_tiles(index)
                    if len(selected_tiles) == 2:
                        check_match()
                        draw_tiles()
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 16.")


def reset_game():
    global tiles, selected_tiles, matching_tiles, start_time, player_timers, player_scores, current_player, pairs_found, game_start_time
    tiles = []
    for color in colors * 2:  # Duplicate each color to create pairs
        tiles.append((color, False, None))  # False indicates unmatched
    random.shuffle(tiles)
    selected_tiles = []
    matching_tiles = []
    pairs_found = 0
    start_time = [time.time(), 0]  # Reset start times for both players
    player_timers = [0, 0]  # Reset timers for both players
    player_scores = [0, 0]  # Reset scores for both players
    current_player = 1  # Reset to start with Player 1
    draw_tiles()
    if is_attack_mode:
        game_start_time = time.time()
    if is_wild_mode:
        initialize_wild_mode()


def initialize_wild_mode():
    global tiles
    tiles = load_images(image_paths)
    random.shuffle(tiles)


def wild_mode_check_match():
    global pairs_found
    if len(selected_tiles) == 2:
        idx1, idx2 = selected_tiles
        names = [tiles[idx1][2], tiles[idx2][2]]
        print(names)
        if names[0] == names[1]:
            tiles[idx1] = (tiles[idx1][0], True, tiles[idx1][2])
            tiles[idx2] = (tiles[idx2][0], True, tiles[idx2][2])
            matching_tiles.extend([idx1, idx2])
            play_match_correct_sound()
            pairs_found += 1
            player_scores[current_player - 1] += 1
            if pairs_found == len(tiles) // 2:
                handle_game_won()
        else:
            # Reveal the second selected tile before hiding both
            play_not_match_sound()
            draw_tiles()
            pygame.time.wait(400)  # Delay to show cards
        selected_tiles.clear()


num_players = draw_player_selection()
game_start_time = time.time()
start_time = [time.time(), 0]  # Start time for Player 1, Player 2 doesn't start until it's their turn

thread = threading.Thread(target=start_listening, args=(user_text,))

if is_voice_control:
    print("Starting voice control...")
    thread.daemon = True
    thread.start()

if is_wild_mode:
    print("Starting wild mode...")
    initialize_wild_mode()

running = True
while running:
    update_timers()
    if is_voice_control:
        voice_control_main_loop()
    if time.time() - game_start_time >= initial_attack_mode_time and is_attack_mode:
        print("Attack mode time is up!")
        print("Player lost!")
        player_won = False
        handle_game_lost_attack_mode()
        # game_start_time = time.time()
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
                if col > 3 or row > 3:
                    continue
                index = row * 4 + col
                if 0 <= index < len(tiles):
                    reveal_tiles(index)
                    if len(selected_tiles) == 2:
                        if is_wild_mode:
                            wild_mode_check_match()
                        else:
                            check_match()

        draw_tiles()


pygame.quit()
if is_voice_control:
    stop_listening()
