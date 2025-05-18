import pygame
import time
import random

# Initialize Pygame
pygame.init()

# Game window size
width, height = 600, 400
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("🐍 Snake Game - Enhanced")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (30, 144, 255)
DARK_GREEN = (0, 155, 0)
YELLOW = (255, 215, 0)

# Snake settings
block_size = 20
snake_speed = 12

clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)
big_font = pygame.font.SysFont("consolas", 40)


def draw_grid():
    for x in range(0, width, block_size):
        pygame.draw.line(win, GRAY, (x, 0), (x, height))
    for y in range(0, height, block_size):
        pygame.draw.line(win, GRAY, (0, y), (width, y))


def draw_snake(snake_list):
    for segment in snake_list:
        pygame.draw.rect(win, DARK_GREEN, [segment[0], segment[1], block_size, block_size], border_radius=5)


def draw_food(x, y):
    pygame.draw.ellipse(win, YELLOW, [x, y, block_size, block_size])


def show_score(score):
    value = font.render(f"Score: {score}", True, BLACK)
    win.blit(value, [10, 10])


def show_game_over(score):
    win.fill(WHITE)
    msg1 = big_font.render("Game Over!", True, RED)
    msg2 = font.render("Press C to Play Again or Q to Quit", True, BLACK)
    msg3 = font.render(f"Final Score: {score}", True, BLUE)
    win.blit(msg1, [width // 2 - 120, height // 3])
    win.blit(msg3, [width // 2 - 80, height // 3 + 50])
    win.blit(msg2, [width // 2 - 160, height // 3 + 100])
    pygame.display.update()


def game_loop():
    game_over = False
    game_close = False

    x = width // 2
    y = height // 2
    x_change = 0
    y_change = 0

    snake_list = []
    snake_length = 1

    food_x = random.randrange(0, width - block_size, block_size)
    food_y = random.randrange(0, height - block_size, block_size)

    while not game_over:

        while game_close:
            show_game_over(snake_length - 1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and x_change == 0:
                    x_change = -block_size
                    y_change = 0
                elif event.key == pygame.K_RIGHT and x_change == 0:
                    x_change = block_size
                    y_change = 0
                elif event.key == pygame.K_UP and y_change == 0:
                    y_change = -block_size
                    x_change = 0
                elif event.key == pygame.K_DOWN and y_change == 0:
                    y_change = block_size
                    x_change = 0

        # Boundary collision
        if x >= width or x < 0 or y >= height or y < 0:
            game_close = True

        x += x_change
        y += y_change

        win.fill(WHITE)
        draw_grid()
        draw_food(food_x, food_y)

        snake_head = [x, y]
        snake_list.append(snake_head)

        if len(snake_list) > snake_length:
            del snake_list[0]

        # Self-collision
        for segment in snake_list[:-1]:
            if segment == snake_head:
                game_close = True

        draw_snake(snake_list)
        show_score(snake_length - 1)

        pygame.display.update()

        # Food collision
        if x == food_x and y == food_y:
            food_x = random.randrange(0, width - block_size, block_size)
            food_y = random.randrange(0, height - block_size, block_size)
            snake_length += 1

        clock.tick(snake_speed)

    pygame.quit()
    quit()


# Start game
game_loop()
