import os
import sys
import math
import random
import time
import tty
import termios

# ————— Константы карты и экрана —————
MAP_W, MAP_H = 20, 20         # размеры карты
SCREEN_W, SCREEN_H = 60, 24   # размеры консоли (колонки × строки)
FOV = math.pi / 3             # угол обзора (60°)
DEPTH = 16                    # дальность прорисовки

# ————— Генерация карты —————
def generate_map():
    m = [['#'] * MAP_W for _ in range(MAP_H)]
    for y in range(1, MAP_H-1):
        for x in range(1, MAP_W-1):
            m[y][x] = '.' if random.random() > 0.3 else '#'
    return m

# ————— Неблокирующий ввод из терминала —————
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# ————— Инициализация —————
world_map = generate_map()
# Найти случайную свободную точку
def find_free():
    while True:
        x, y = random.randint(1, MAP_W-2), random.randint(1, MAP_H-2)
        if world_map[y][x] == '.':
            return x, y

player_x, player_y = find_free()
player_a = 0.0  # угол взгляда

# Ключи и выход
NUM_KEYS = 3
keys = set(find_free() for _ in range(NUM_KEYS))
exit_pos = find_free()
collected = 0

# ————— Функция рендера кадра —————
def render_frame():
    os.system('cls' if os.name=='nt' else 'clear')

    # Рисуем псевдо-3D
    for cols in range(SCREEN_W):
        ray_angle = (player_a - FOV/2.0) + (cols / SCREEN_W) * FOV
        distance_to_wall = 0
        hit = False

        eye_x = math.sin(ray_angle)
        eye_y = math.cos(ray_angle)

        # шагаем по лучу
        while not hit and distance_to_wall < DEPTH:
            distance_to_wall += 0.1
            tx = int(player_x + eye_x * distance_to_wall)
            ty = int(player_y + eye_y * distance_to_wall)
            if tx < 0 or tx >= MAP_W or ty < 0 or ty >= MAP_H:
                hit = True
                distance_to_wall = DEPTH
            elif world_map[ty][tx] == '#':
                hit = True

        # вычисляем высоту стены
        ceiling = int((SCREEN_H / 2.0) - SCREEN_H / distance_to_wall)
        floor = SCREEN_H - ceiling

        # выбираем символ по дистанции
        shade = ' '
        if distance_to_wall <= DEPTH / 4.0:      shade = '█'
        elif distance_to_wall < DEPTH / 3.0:     shade = '▓'
        elif distance_to_wall < DEPTH / 2.0:     shade = '▒'
        elif distance_to_wall < DEPTH:           shade = '·'
        else:                                    shade = ' '

        # рисуем столбец
        for row in range(SCREEN_H):
            if row < ceiling:
                sys.stdout.write(' ')
            elif row > ceiling and row <= floor:
                sys.stdout.write(shade)
            else:
                sys.stdout.write('.')
        sys.stdout.write('\n')

    # Статус и мини-карта
    print(f"Ключи: {collected}/{NUM_KEYS}    Прицел: (^)\n")
    for y in range(MAP_H):
        line = ''
        for x in range(MAP_W):
            if int(player_x)==x and int(player_y)==y:
                line += 'P'
            elif (x, y) in keys:
                line += 'K'
            elif (x, y) == exit_pos:
                line += 'E'
            else:
                line += world_map[y][x]
        print(line)
    print("\nW/S — вперёд/назад | A/D — поворот | Q — выход")

# ————— Основной цикл игры —————
def game_loop():
    global player_x, player_y, player_a, collected

    while True:
        render_frame()

        # Проверка на взятие ключа / выход
        pos = (int(player_x), int(player_y))
        if pos in keys:
            keys.remove(pos)
            collected += 1
        if collected == NUM_KEYS and pos == exit_pos:
            print("\n🎉 Все ключи собраны и выход открыт! Вы выиграли! 🎉")
            break

        cmd = getch().lower()
        if cmd == 'q':
            break
        # движение
        elif cmd == 'w':
            player_x += math.sin(player_a) * 0.5
            player_y += math.cos(player_a) * 0.5
            if world_map[int(player_y)][int(player_x)] == '#':
                player_x -= math.sin(player_a) * 0.5
                player_y -= math.cos(player_a) * 0.5
        elif cmd == 's':
            player_x -= math.sin(player_a) * 0.5
            player_y -= math.cos(player_a) * 0.5
            if world_map[int(player_y)][int(player_x)] == '#':
                player_x += math.sin(player_a) * 0.5
                player_y += math.cos(player_a) * 0.5
        # поворот
        elif cmd == 'a':
            player_a -= 0.1
        elif cmd == 'd':
            player_a += 0.1

if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        pass
