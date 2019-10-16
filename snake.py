import pygame
import math
import random


snake_coords = []
# directions
RIGHT = 'RIGHT'
RIGHT_UP = 'RIGHT_UP'
RIGHT_DOWN = 'RIGHT_DOWN'
LEFT = 'LEFT'
LEFT_UP = 'LEFT_UP'
LEFT_DOWN = 'LEFT_DOWN'
DOWN = 'DOWN'
UP = 'UP'
# math constants
cos60 = 0.5
sin60 = math.sin(math.radians(60))
# flags
APPLE_EATEN = 0
GAME_OVER = 1
SUCCESSFULLY_MOVED = 2
TRIANGULAR = 3
HEXAGONAL = 4


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


def get_vertices_triangle(x, y, side):
    if (x + y) % 2 == 1:
        coords = ((0, 0), (cos60, sin60), (1, 0))
    else:
        coords = ((0, sin60), (cos60, 0), (1, sin60))
    result = []
    for ex_x, ex_y in coords:
        result.append(((ex_x + (x/2)) * side, (ex_y + (y * sin60)) * side))
    return result


def get_vertices_hexagon(x, y, side):
    if x % 2 == 1:
        coords = ((0, 2 * sin60), (cos60, sin60), (1 + cos60, sin60),
                  (2, 2 * sin60), (1 + cos60, 3 * sin60), (cos60, 3 * sin60))
    else:
        coords = ((0, sin60), (cos60, 0), (1 + cos60, 0),
                  (2, sin60), (1 + cos60, 2 * sin60), (cos60, 2 * sin60))
    result = []
    for ex_x, ex_y in coords:
        result.append(((ex_x + (x / 2 * 3)) * side, (ex_y + (y * 2 * sin60)) * side))
    return result


def get_coords_triangle_snake(x, y, side):
    r = math.sqrt(3) / 6
    if (x + y) % 2 == 1:
        return (int((x + 1) * cos60 * side), int((y * sin60 + r) * side)), int(r * side)
    else:
        return (int((x + 1) * cos60 * side), int(((y + 1) * sin60 - r) * side)), int(r * side)


def get_coords_hexagonal_snake(x, y, side):
    r = sin60
    if x % 2 == 0:
        return (int((x * (1 + cos60) + 1) * side), int((y * 2 * sin60 + sin60) * side)), int(r * side)
    else:
        return (int((x * (1 + cos60) + 1) * side), int((y + 1) * 2 * sin60 * side)), int(r * side)


def triangular_grid_size(width, height, side):
    return (width + 1) * cos60 * side, height * sin60 * side


def hexagonal_grid_size(width, height, side):
    return (width * (1 + cos60) + cos60) * side, (height * 2 * sin60 + sin60) * side


def create_horizontal_grid(grid_type, width, height, side, torus=True):
    if grid_type == TRIANGULAR:
        grid_size = triangular_grid_size
        get_vertices = get_vertices_triangle
        h_cells = int(height / 2) * 2
        w_cells = int(width / 2) * 2
        if not torus:
            w_cells += 1
    else:
        grid_size = hexagonal_grid_size
        get_vertices = get_vertices_hexagon
        h_cells = height
        if torus:
            w_cells = int(width / 2) * 2
        else:
            w_cells = width
    grid = pygame.Surface(grid_size(w_cells, h_cells, side), pygame.SRCALPHA)
    grid.fill(pygame.Color('black'))
    for h in range(h_cells):
        for w in range(w_cells):
            vertices = get_vertices(w, h, side)
            pygame.draw.polygon(grid, pygame.Color('green'), vertices)
            pygame.draw.polygon(grid, pygame.Color('black'), vertices, 1)
    return grid, (w_cells, h_cells)


def draw_snake(context, side, grid_type):
    if grid_type == TRIANGULAR:
        get_coords_snake = get_coords_triangle_snake
    else:
        get_coords_snake = get_coords_hexagonal_snake
    first = True
    for coords in snake_coords:
        if first:
            c = pygame.Color('black')
            first = False
        else:
            c = pygame.Color('white')
        pygame.draw.circle(context, c, *get_coords_snake(*coords, side))


def create_next_coords(coords, direction):
    x, y = coords
    even_column = False
    if x % 2 == 1:
        even_column = True
    if direction == RIGHT:
        return [x + 1, y]
    elif direction == LEFT:
        return [x - 1, y]
    elif direction == DOWN:
        return [x, y + 1]
    elif direction == UP:
        return [x, y - 1]
    elif direction == RIGHT_UP:
        if even_column:
            return [x + 1, y]
        else:
            return [x + 1, y - 1]
    elif direction == RIGHT_DOWN:
        if even_column:
            return [x + 1, y + 1]
        else:
            return [x + 1, y]
    elif direction == LEFT_DOWN:
        if even_column:
            return [x - 1, y + 1]
        else:
            return [x - 1, y]
    elif direction == LEFT_UP:
        if even_column:
            return [x - 1, y]
        else:
            return [x - 1, y - 1]


def find_direction(begin, end, grid_type):
    if grid_type == TRIANGULAR:
        movements = [LEFT, RIGHT, UP, DOWN]
    else:
        movements = [LEFT_UP, LEFT_DOWN, RIGHT_UP, RIGHT_DOWN, DOWN, UP]
    for move in movements:
        if create_next_coords(begin, move) == end:
            return move


def move_snake(direction, apple_coords, grid_type, grid_size=None, torus=False):
    if grid_type == TRIANGULAR:
        # solving the control problem
        if direction == DOWN and (snake_coords[0][0] + snake_coords[0][1]) % 2 == 1:
            if create_next_coords(snake_coords[0], LEFT) == snake_coords[1]:
                direction = RIGHT
            else:
                direction = LEFT
        if direction == UP and (snake_coords[0][0] + snake_coords[0][1]) % 2 == 0:
            if create_next_coords(snake_coords[0], RIGHT) == snake_coords[1]:
                direction = LEFT
            else:
                direction = RIGHT
    # finding out next coords of head
    next_coords = create_next_coords(snake_coords[0], direction)
    # the snake hit the wall?
    if next_coords[0] < 0 or next_coords[0] >= grid_size[0] or \
            next_coords[1] < 0 or next_coords[1] >= grid_size[1]:
        if torus:
            if next_coords[0] >= grid_size[0]:
                next_coords[0] = 0
            elif next_coords[0] < 0:
                next_coords[0] = grid_size[0] - 1
            if next_coords[1] >= grid_size[1]:
                next_coords[1] = 0
            elif next_coords[1] < 0:
                next_coords[1] = grid_size[1] - 1
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
            new_dir = find_direction(snake_coords[-2], snake_coords[-1], grid_type)
            snake_coords.reverse()
            return new_dir
        # body
        else:
            snake_coords.append(tail)
            return GAME_OVER
    snake_coords.insert(0, next_coords)
    return SUCCESSFULLY_MOVED


def create_apple(grid_size):
    all_coords = []
    for y in range(grid_size[1]):
        for x in range(grid_size[0]):
            if [x, y] not in snake_coords:
                all_coords.append([x, y])
    return random.choice(all_coords)


def draw_apple(context, coords, side, grid_type):
    if grid_type == TRIANGULAR:
        get_coords_apple = get_coords_triangle_snake
    else:
        get_coords_apple = get_coords_hexagonal_snake
    pygame.draw.circle(context, pygame.Color('red'), *get_coords_apple(*coords, side))


def centered_blit(img, box):
    x = (box.get_width() - img.get_width())/2
    y = (box.get_height() - img.get_height())/2
    return x, y


def create_game_over_surface(font1, font2):
    text1 = font1.render("Game over", True, pygame.Color('red'))
    text2 = font2.render("Press R to restart", True, pygame.Color('red'))
    w = max(text1.get_width(), text2.get_width())
    h = text1.get_height() + text2.get_height()
    result = pygame.Surface((int(w * 1.2), int(h * 1.2)))
    rx1, ry1 = centered_blit(text1, result)
    result.blit(text1, (rx1, ry1 - text2.get_height() / 2))
    rx2, ry2 = centered_blit(text2, result)
    result.blit(text2,  (rx2, ry2 + text2.get_height() / 2))
    return result


def find_side(context_size, grid_width, grid_height, grid_type):
    w, h = context_size
    result = max(w/grid_width, h/grid_height)
    if grid_type == TRIANGULAR:
        return result * 2
    else:
        return result


def main():
    pygame.init()
    win = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Grids")
    font1 = pygame.font.SysFont('serif', int(win.get_width() / 20))
    font2 = pygame.font.SysFont('serif', int(win.get_width() / 30))
    font3 = pygame.font.SysFont('serif', int(win.get_width() / 40))
    game_over_surface = create_game_over_surface(font1, font2)
    grid_type = HEXAGONAL
    pygame_open = True
    while pygame_open:
        if grid_type == HEXAGONAL:
            grid_width = 20
            grid_height = 9
        else:
            grid_width = 24
            grid_height = 8
        side = find_side(win.get_size(), grid_width, grid_height, grid_type)
        clear_grid, grid_size = create_horizontal_grid(grid_type, grid_width, grid_height, side)
        game_surface = pygame.Surface((win.get_width(), win.get_height()-font3.get_height()))
        snake_coords.clear()
        snake_coords.extend([[2, 0], [1, 0], [0, 0]])
        if grid_type == TRIANGULAR:
            snake_move = RIGHT
        else:
            snake_move = RIGHT_DOWN
        apple_coords = create_apple(grid_size)
        score = 0
        restart_waiting = True
        game = True
        while game:
            pygame.time.Clock().tick(5)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        restart_waiting = False
                        game = False
                        if grid_type == HEXAGONAL:
                            grid_type = TRIANGULAR
                        else:
                            grid_type = HEXAGONAL
                    if event.key == pygame.K_w:
                        snake_move = UP
                    if event.key == pygame.K_s:
                        snake_move = DOWN
                    if grid_type == TRIANGULAR:
                        if event.key == pygame.K_a:
                            snake_move = LEFT
                        if event.key == pygame.K_d:
                            snake_move = RIGHT
                    elif grid_type == HEXAGONAL:
                        if event.key == pygame.K_q:
                            snake_move = LEFT_UP
                        if event.key == pygame.K_a:
                            snake_move = LEFT_DOWN
                        if event.key == pygame.K_e:
                            snake_move = RIGHT_UP
                        if event.key == pygame.K_d:
                            snake_move = RIGHT_DOWN
            result = move_snake(snake_move, apple_coords, grid_type, grid_size, True)
            if type(result) == str:
                snake_move = result
            elif result == APPLE_EATEN:
                score += 1
                apple_coords = create_apple(grid_size)
            elif result == GAME_OVER:
                game = False
            grid = clear_grid.copy()
            score_text = font3.render('score:' + str(score), True, pygame.Color('black'))
            remark_text = font3.render('You can press G, after which the grid will change and the game will restart',
                                       True, pygame.Color('black'))
            win.fill(pygame.Color('white'))
            draw_apple(grid, apple_coords, side, grid_type)
            draw_snake(grid, side, grid_type)
            grid = aspect_scale(grid, game_surface)
            game_surface.blit(grid, centered_blit(grid, game_surface))
            win.blit(game_surface, (0, font3.get_height()))
            win.blit(score_text, (10, 0))
            win.blit(remark_text, (win.get_width() - remark_text.get_width() - 10, 0))
            pygame.display.update()
        while restart_waiting:
            win.blit(game_over_surface, centered_blit(game_over_surface, win))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        restart_waiting = False
                    if event.key == pygame.K_g:
                        restart_waiting = False
                        if grid_type == HEXAGONAL:
                            grid_type = TRIANGULAR
                        else:
                            grid_type = HEXAGONAL


if __name__ == '__main__':
    main()
