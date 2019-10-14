import pygame
import math
import random


grid_for_snake = []
snake_coords = []
triangular_side = 100

RIGHT = [0, 1]
LEFT = [0, -1]
DOWN = [1, 0]
UP = [-1, 0]

APPLE_EATEN = 0
GAME_OVER = 1
SUCCESSFULLY_MOVED = 2


def aspect_scale(img, box):
    bx, by = box.get_size()
    ix, iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.smoothscale(img, (int(sx), int(sy)))


def right_coords(coords):
    return [int(coords[0]*triangular_side), int(coords[1]*triangular_side)]


def create_horizontal_triangular_grid(width, height, torus=True):
    grid_for_snake.clear()
    cos60 = 0.5
    sin60 = math.sin(math.radians(60))
    # the radius of the inscribed circle
    r = math.sqrt(3) / 6
    h_cells = int(height / 2) * 2
    w_cells = int(width / 2) * 2
    if not torus:
        w_cells += 1
    grid = pygame.Surface(right_coords(((w_cells + 1) * cos60, h_cells * sin60)), pygame.SRCALPHA)
    grid.fill(pygame.Color('black'))
    # /1\2/
    # \3/4\
    coords12 = [(0, sin60), (cos60, 0), (1, sin60)]
    coords34 = [(0, sin60), (cos60, 2*sin60), (1, sin60)]
    for h in range(h_cells):
        if h % 2 == 1:
            coords = list(map(lambda a: (a[0], a[1] + ((h-1)*sin60)), coords34))
        else:
            coords = list(map(lambda a: (a[0], a[1] + (h*sin60)), coords12))
        line = []
        for w in range(w_cells):
            if (w+h) % 2 == 1:
                line.append(right_coords(((w + 1) * cos60, h * sin60 + r)))
            else:
                line.append(right_coords(((w + 1) * cos60, (h + 1) * sin60 - r)))
            pygame.draw.polygon(grid, pygame.Color('green'), list(map(right_coords, coords)))
            pygame.draw.polygon(grid, pygame.Color('black'), list(map(right_coords, coords)), 1)
            coords.pop(0)
            coords.append((coords[0][0] + 1, coords[0][1]))
        grid_for_snake.append(line)
    return grid, right_coords((r, 0))[0]


def draw_snake(context, r):
    first = True
    for coords in snake_coords:
        if first:
            c = pygame.Color('black')
            first = False
        else:
            c = pygame.Color('white')
        pygame.draw.circle(context, c, grid_for_snake[coords[0]][coords[1]], r)


def create_next_coords(direction):
    return [snake_coords[0][0] + direction[0], snake_coords[0][1] + direction[1]]


def find_direction(begin, end):
    result = [begin[0] - end[0], begin[1] - end[1]]
    for i in range(len(result)):
        if abs(result[i]) > 1:
            if result[i] < 0:
                result[i] = 1
            else:
                result[i] = -1
    return result


def move_snake(direction, apple_coords, torus=True):
    if direction == DOWN and (snake_coords[0][0] + snake_coords[0][1]) % 2 == 1:
        if create_next_coords(LEFT) == snake_coords[1]:
            direction = RIGHT
        else:
            direction = LEFT
    if direction == UP and (snake_coords[0][0] + snake_coords[0][1]) % 2 == 0:
        if create_next_coords(RIGHT) == snake_coords[1]:
            direction = LEFT
        else:
            direction = RIGHT
    # finding out next coords of head
    next_coords = create_next_coords(direction)
    # torus things
    if next_coords[0] < 0 or next_coords[0] >= len(grid_for_snake) or \
            next_coords[1] < 0 or next_coords[1] >= len(grid_for_snake[0]):
        if torus:
            if next_coords[0] >= len(grid_for_snake):
                next_coords[0] = 0
            elif next_coords[0] < 0:
                next_coords[0] = len(grid_for_snake) - 1
            if next_coords[1] >= len(grid_for_snake[0]):
                next_coords[1] = 0
            elif next_coords[1] < 0:
                next_coords[1] = len(grid_for_snake[0]) - 1
        else:
            return GAME_OVER
    # apple
    if next_coords == apple_coords:
        snake_coords.insert(0, next_coords)
        return APPLE_EATEN
    # snake crashed into itself?
    tail = snake_coords.pop()
    if next_coords in snake_coords:
        # neck
        if next_coords == snake_coords[1]:
            # turn snake
            snake_coords.append(tail)
            new_dir = find_direction(snake_coords[-1], snake_coords[-2])
            snake_coords.reverse()
            return new_dir
        # body
        else:
            snake_coords.append(tail)
            return GAME_OVER
    snake_coords.insert(0, next_coords)
    return SUCCESSFULLY_MOVED


def create_apple():
    all_coords = []
    for y in range(len(grid_for_snake[0])):
        for x in range(len(grid_for_snake)):
            if [x, y] not in snake_coords:
                all_coords.append([x, y])
    return random.choice(all_coords)


def draw_apple(context, coords, r):
    pygame.draw.circle(context, pygame.Color('red'), grid_for_snake[coords[0]][coords[1]], r)


def centered_blit(img, box):
    x = (box.get_width() - img.get_width())/2
    y = (box.get_height() - img.get_height())/2
    return x, y


def create_game_over_surface(font1, font2):
    text1 = font1.render("Game over", True, pygame.Color('red'))
    text2 = font2.render("Press R to restart", True, pygame.Color('red'))
    w = max(text1.get_width(), text2.get_width())
    h = text1.get_height() + text2.get_height()
    result = pygame.Surface((w + 50, h + 50))
    rx1, ry1 = centered_blit(text1, result)
    result.blit(text1, (rx1, ry1 - text2.get_height() / 2))
    rx2, ry2 = centered_blit(text2, result)
    result.blit(text2,  (rx2, ry2 + text2.get_height() / 2))
    return result


def find_triangular_side(display, w, h):
    x, y = display.get_size()
    global triangular_side
    triangular_side = max(x/w, y/h)


def main():
    pygame.init()
    win = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Grids")
    font1 = pygame.font.SysFont('serif', int(win.get_width() / 20))
    font2 = pygame.font.SysFont('serif', int(win.get_width() / 30))
    font3 = pygame.font.SysFont('serif', int(win.get_width() / 40))
    game_over_surface = create_game_over_surface(font1, font2)
    pygame_open = True
    while pygame_open:
        grid_width = 24
        grid_height = 9
        find_triangular_side(win, grid_width, grid_height)
        clear_grid, r = create_horizontal_triangular_grid(grid_width, grid_height)
        game_surface = pygame.Surface((win.get_width(), win.get_height()-font3.get_height()))
        snake_coords.clear()
        snake_coords.extend([[0, 2], [0, 1], [0, 0]])
        snake_move = RIGHT
        apple_coords = create_apple()
        score = 0
        game = True
        while game:
            pygame.time.Clock().tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        snake_move = UP
                    if event.key == pygame.K_s:
                        snake_move = DOWN
                    if event.key == pygame.K_a:
                        snake_move = LEFT
                    if event.key == pygame.K_d:
                        snake_move = RIGHT
            result = move_snake(snake_move, apple_coords)
            if type(result) == list:
                snake_move = result
            elif result == APPLE_EATEN:
                score += 1
                apple_coords = create_apple()
            elif result == GAME_OVER:
                game = False
            grid = clear_grid.copy()
            score_text = font3.render('score:' + str(score), True, pygame.Color('black'))
            win.fill(pygame.Color('white'))
            draw_apple(grid, apple_coords, r)
            draw_snake(grid, r)
            grid = aspect_scale(grid, game_surface)
            game_surface.blit(grid, centered_blit(grid, game_surface))
            win.blit(game_surface, (0, font3.get_height()))
            win.blit(score_text, (10, 0))
            pygame.display.update()
        win.blit(game_over_surface, centered_blit(game_over_surface, win))
        pygame.display.update()
        restart_waiting = True
        while restart_waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    restart_waiting = False


if __name__ == '__main__':
    main()
