import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions and title
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Memory Game")

# Colors
BACKGROUND_COLOR = (30, 30, 30)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
colors = [
    (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
    (255, 100, 255), (100, 255, 255), (255, 140, 0), (140, 70, 20)
]

# Game variables
tile_width = 100
tile_height = 100
tile_margin = 20
tiles = []  # (color, matched)
selected_tiles = []
matching_tiles = []

# Initialize tiles
for color in colors * 2:  # Duplicate each color to create pairs
    tiles.append((color, False))  # False indicates unmatched
random.shuffle(tiles)


def draw_tiles():
    screen.fill(BACKGROUND_COLOR)
    for i, (color, matched) in enumerate(tiles):
        row = i // 4
        col = i % 4
        x = col * (tile_width + tile_margin) + tile_margin
        y = row * (tile_height + tile_margin) + tile_margin

        if i in selected_tiles or matched:
            pygame.draw.rect(screen, color, (x, y, tile_width, tile_height))
        else:
            pygame.draw.rect(screen, GRAY, (x, y, tile_width, tile_height))

        # Draw border for aesthetic purposes
        pygame.draw.rect(screen, WHITE, (x, y, tile_width, tile_height), 3)

    pygame.display.flip()


def reveal_tiles(index):
    if tiles[index][1] == False and index not in selected_tiles:
        selected_tiles.append(index)


def check_match():
    if len(selected_tiles) == 2:
        idx1, idx2 = selected_tiles
        if tiles[idx1][0] == tiles[idx2][0]:
            tiles[idx1] = (tiles[idx1][0], True)
            tiles[idx2] = (tiles[idx2][0], True)
            matching_tiles.extend([idx1, idx2])
        else:
            # Reveal the second selected tile before hiding both
            draw_tiles()
            pygame.time.wait(1000)  # Delay to show cards
        selected_tiles.clear()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and len(selected_tiles) < 2:
            x, y = pygame.mouse.get_pos()
            col = x // (tile_width + tile_margin)
            row = y // (tile_height + tile_margin)
            index = row * 4 + col
            if index < len(tiles):
                reveal_tiles(index)
                if len(selected_tiles) == 2:
                    check_match()

    draw_tiles()

pygame.quit()
