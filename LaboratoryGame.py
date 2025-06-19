import pygame
import math
import random
import sys

# Инициализация
pygame.init()
WIDTH, HEIGHT = 800, 600
HALF_HEIGHT = HEIGHT // 2
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Побег из Лаборатории")

MAP_WIDTH, MAP_HEIGHT = 16, 16
TILE = 50
FOV = math.pi / 3
NUM_RAYS = 120
MAX_DEPTH = 800
DELTA_ANGLE = FOV / NUM_RAYS
SCALE = WIDTH // NUM_RAYS

# Цвета
WHITE = (255, 255, 255)
DARK_GRAY = (30, 30, 30)
BLUE = (0, 0, 200)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLACK = (0, 0, 0)

# Генерация карты
def generate_map():
    m = [['#' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    for y in range(1, MAP_HEIGHT - 1):
        for x in range(1, MAP_WIDTH - 1):
            m[y][x] = '.' if random.random() > 0.2 else '#'
    return m

world_map = generate_map()

def find_free():
    while True:
        x, y = random.randint(1, MAP_WIDTH - 2), random.randint(1, MAP_HEIGHT - 2)
        if world_map[y][x] == '.':
            return x, y

player_x, player_y = find_free()
player_angle = 0

NUM_KEYS = 3
keys = set(find_free() for _ in range(NUM_KEYS))
exit_pos = find_free()
collected = 0

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

def draw_minimap():
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            color = DARK_GRAY if world_map[y][x] == '#' else WHITE
            pygame.draw.rect(screen, color, (x * 10, y * 10, 10, 10))
    pygame.draw.circle(screen, RED, (int(player_x * 10), int(player_y * 10)), 5)
    for kx, ky in keys:
        pygame.draw.circle(screen, GREEN, (kx * 10, ky * 10), 4)
    pygame.draw.circle(screen, BLUE, (exit_pos[0] * 10, exit_pos[1] * 10), 4)

def cast_rays():
    ox = player_x * TILE
    oy = player_y * TILE
    cur_angle = player_angle - FOV / 2
    for ray in range(NUM_RAYS):
        sin_a = math.sin(cur_angle)
        cos_a = math.cos(cur_angle)

        for depth in range(1, MAX_DEPTH, 4):
            x = ox + depth * cos_a
            y = oy + depth * sin_a

            map_x = int(x / TILE)
            map_y = int(y / TILE)

            if map_x < 0 or map_y < 0 or map_x >= MAP_WIDTH or map_y >= MAP_HEIGHT:
                break
            if world_map[map_y][map_x] == '#':
                depth *= math.cos(player_angle - cur_angle)
                proj_height = 50000 / (depth + 0.0001)
                color = 255 / (1 + depth * depth * 0.0001)
                shade = (color, color, color)
                pygame.draw.rect(screen, shade, (ray * SCALE, HALF_HEIGHT - proj_height // 2, SCALE, proj_height))
                break
        cur_angle += DELTA_ANGLE

def draw_interface():
    text = font.render(f"Ключи: {collected}/{NUM_KEYS}", True, WHITE)
    screen.blit(text, (10, HEIGHT - 40))
    pygame.draw.line(screen, RED, (WIDTH // 2 - 5, HALF_HEIGHT), (WIDTH // 2 + 5, HALF_HEIGHT), 2)

def game_loop():
    global player_x, player_y, player_angle, collected

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

        # Движение
        keys_pressed = pygame.key.get_pressed()
        speed = 0.05
        rot_speed = 0.04

        if keys_pressed[pygame.K_w]:
            dx = math.cos(player_angle) * speed
            dy = math.sin(player_angle) * speed
            if world_map[int(player_y + dy)][int(player_x + dx)] == '.':
                player_x += dx
                player_y += dy
        if keys_pressed[pygame.K_s]:
            dx = -math.cos(player_angle) * speed
            dy = -math.sin(player_angle) * speed
            if world_map[int(player_y + dy)][int(player_x + dx)] == '.':
                player_x += dx
                player_y += dy
        if keys_pressed[pygame.K_a]:
            player_angle -= rot_speed
        if keys_pressed[pygame.K_d]:
            player_angle += rot_speed

        # Проверка ключей и выхода
        pos = (int(player_x), int(player_y))
        if pos in keys:
            keys.remove(pos)
            collected += 1
        if collected == NUM_KEYS and pos == exit_pos:
            print("🎉 Победа! Все ключи собраны и выход найден!")
            pygame.quit()
            sys.exit()

        # Рендер
        screen.fill(BLACK)
        cast_rays()
        draw_interface()
        draw_minimap()
        pygame.display.flip()
        clock.tick(60)

# Запуск игры
game_loop()
