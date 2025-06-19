import os
import sys
import math
import random
import time

# ============ КРОСС-ПЛАТФОРМЕННЫЙ ВВОД ============
is_windows = os.name == 'nt'
if is_windows:
    import msvcrt
else:
    import tty
    import termios

def getch():
    if is_windows:
        return msvcrt.getch().decode('utf-8').lower()
    else:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch.lower()

# ============ КОНСТАНТЫ ============
MAP_W, MAP_H = 20, 20
SCREEN_W, SCREEN_H = 60, 24
FOV = math.pi / 3
DEPTH = 16

# ============ КАРТА ============
def generate_map():
    m = [['#'] * MAP_W for _ in range(MAP_H)]
    for y in range(1, MAP_H - 1):
        for x in range(1, MAP_W - 1):
            m[y][x] = '.' if random.random() > 0.3 else '#'
    return m

world_map = generate_map()

def find_free():
    while True:
        x, y = random.randint(1, MAP_W - 2), random.randint(1, MAP_H - 2)
        if world_map[y][x] == '.':
            return x, y

player_x, player_y = find_free()
player_a = 0.0

NUM_KEYS = 3
keys = set(find_free() for _ in range(NUM_KEYS))
exit_pos = find_free()
collected = 0

# ============ ОЧИСТКА ЭКРАНА ============
def clear():
    os.system('cls' if is_windows else 'clear')

# ============ РЕНДЕР ЭКРАНА ============
def render_frame():
    clear()
    for col in range(SCREEN_W):
        ray_angle = (player_a - FOV / 2.0) + (col / SCREEN_W) * FOV
        distance_to_wall = 0
        hit = False
        eye_x = math.sin(ray_angle)
        eye_y = math.cos(ray_angle)

        while not hit and distance_to_wall < DEPTH:
            distance_to_wall += 0.1
            tx = int(player_x + eye_x * distance_to_wall)
            ty = int(player_y + eye_y * distance_to_wall)
            if tx < 0 or tx >= MAP_W or ty < 0 or ty >= MAP_H:
                hit = True
                distance_to_wall = DEPTH
            elif world_map[ty][tx] == '#':
                hit = True

        ceiling = int((SCREEN_H / 2.0) - SCREEN_H / distance_to_wall)
        floor = SCREEN_H - ceiling

        shade = ' '
        if distance_to_wall <= DEPTH / 4.0:      shade = '█'
        elif distance_to_wall < DEPTH / 3.0:     shade = '▓'
        elif distance_to_wall < DEPTH / 2.0:     shade = '▒'
        elif distance_to_wall < DEPTH:           shade = '·'
        else:                                    shade = ' '

        for row in range(SCREEN_H):
            if row < ceiling:
                sys.stdout.write(' ')
            elif ceiling <= row <= floor:
                sys.stdout.write(shade)
            else:
                sys.stdout.write('.')
        sys.stdout.write('\n')

    print(f"\n🔑 Ключи: {collected}/{NUM_KEYS}  |  🎯 Цель: найти все ключи и дойти до выхода (E)")

    print("\nМини-карта:")
    for y in range(MAP_H):
        line = ''
        for x in range(MAP_W):
            if int(player_x) == x and int(player_y) == y:
                line += 'P'
            elif (x, y) in keys:
                line += 'K'
            elif (x, y) == exit_pos:
                line += 'E'
            else:
                line += world_map[y][x]
        print(line)
    print("\nW/S — вперёд/назад | A/D — поворот | Q — выход")

# ============ ИГРОВОЙ ЦИКЛ ============
def game_loop():
    global player_x, player_y, player_a, collected

    while True:
        render_frame()

        pos = (int(player_x), int(player_y))
        if pos in keys:
            keys.remove(pos)
            collected += 1
        if collected == NUM_KEYS and pos == exit_pos:
            print("\n🎉 Все ключи собраны и выход найден! Победа! 🎉")
            break

        cmd = getch()
        if cmd == 'q':
            print("\nВыход из игры.")
            break
        elif cmd == 'w':
            nx = player_x + math.sin(player_a) * 0.5
            ny = player_y + math.cos(player_a) * 0.5
            if world_map[int(ny)][int(nx)] != '#':
                player_x, player_y = nx, ny
        elif cmd == 's':
            nx = player_x - math.sin(player_a) * 0.5
            ny = player_y - math.cos(player_a) * 0.5
            if world_map[int(ny)][int(nx)] != '#':
                player_x, player_y = nx, ny
        elif cmd == 'a':
            player_a -= 0.1
        elif cmd == 'd':
            player_a += 0.1

# ============ ЗАПУСК ============
if __name__ == "__main__":
    try:
        game_loop()
    except KeyboardInterrupt:
        print("\nИгра прервана.")
