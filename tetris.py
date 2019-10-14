import pygame
import random


class Tetromino:
    down = (0, 1)
    right = (1, 0)
    left = (-1, 0)

    def __init__(self, field_size):
        colors = ('blue', 'red', 'green', 'yellow')
        tetrominos = [([(1, 0), (0, 0), (-1, 0), (-2, 0)],
                       [(0, 1), (0, 0), (0, -1), (0, -2)]),  # I
                      ([(0, 0), (0, -1), (1, 0), (1, -1)],
                       [(0, 0), (0, -1), (1, 0), (1, -1)]),  # O
                      ([(1, 0), (0, 0), (-1, 0), (0, 1)],
                       [(0, -1), (0, 0), (-1, 0), (0, 1)],
                       [(0, -1), (0, 0), (-1, 0), (1, 0)],
                       [(0, -1), (0, 0), (0, 1), (1, 0)]),  # T
                      ([(-1, 0), (0, 0), (1, -1), (1, 0)],
                       [(0, -1), (0, 0), (0, 1), (-1, -1)],
                       [(-1, 0), (0, 0), (-1, 1), (1, 0)],
                       [(0, -1), (0, 0), (0, 1), (1, 1)]),  # J
                      ([(-1, -1), (0, 0), (-1, 0), (1, 0)],
                       [(0, -1), (0, 0), (0, 1), (-1, 1)],
                       [(1, 1), (0, 0), (-1, 0), (1, 0)],
                       [(0, -1), (0, 0), (0, 1), (1, -1)]),  # L
                      ([(0, 0), (-1, 0), (1, 1), (0, 1)],
                       [(0, 0), (1, 0), (0, 1), (1, -1)]),  # S
                      ([(0, 0), (1, 0), (0, 1), (-1, 1)],
                       [(0, 0), (1, 0), (0, -1), (1, 1)])]  # Z
        self.coords = random.choice(tetrominos)
        self.angle = 0
        self.center = (int(field_size[0] / 2), 0)
        self.color = pygame.Color(random.choice(colors))

    def coordinates(self):
        result = []
        for coord in self.coords[self.angle]:
            result.append((coord[0]+self.center[0], coord[1]+self.center[1]))
        return result

    def rotate(self, field_size):
        a = self.angle + 1
        if a == len(self.coords):
            a = 0
        for coord in self.coords[a]:
            for i in range(2):
                if not (0 <= coord[i] + self.center[i] < field_size[i]):
                    return
        self.angle = a

    def correct_direction(self, d):
        if d in (Tetromino.right, Tetromino.left, Tetromino.down):
            return True
        else:
            return False

    def is_blocked(self, field, direction=down):
        for x, y in self.coordinates():
            if (0 <= (x + direction[0]) < len(field)) and (0 <= (y + direction[1]) < len(field[0])):
                if field[x + direction[0]][y + direction[1]] != pygame.Color('white'):
                    return True
            else:
                return True
        return False

    def shift(self, move, field):
        if self.correct_direction(move) and not self.is_blocked(field, move):
            self.center = (self.center[0] + move[0], self.center[1] + move[1])
        else:
            return

    def draw(self, context, cell_size):
        for x, y in self.coordinates():
            pygame.draw.rect(context, self.color, ((x * cell_size, y * cell_size), (cell_size, cell_size)))


def create_field(context, cell_size):
    result = []
    for x in range(int(context.get_width() / cell_size)):
        colmn = []
        for y in range(int(context.get_height() / cell_size)):
            color = pygame.Color('white')
            colmn.append(color)
        result.append(colmn)
    return result


def draw_field(context, field, cell_size):
    for x in range(len(field)):
        for y in range(len(field[0])):
            pygame.draw.rect(context, field[x][y], ((x * cell_size, y * cell_size), (cell_size, cell_size)))
            pygame.draw.rect(context, pygame.Color('black'),
                             ((x * cell_size, y * cell_size), (cell_size, cell_size)), 1)


def field_append_tetromino(tetromino, field):
    for x, y in tetromino.coordinates():
        field[x][y] = tetromino.color


def main():
    pygame.init()
    cell_size = 25
    field_width, field_height = 10, 20
    win = pygame.display.set_mode((field_width * cell_size, field_height * cell_size))
    pygame.display.set_caption("Tetris")
    field = create_field(win, cell_size)
    game = True
    while game:
        t = Tetromino((field_width, field_height))
        while not t.is_blocked(field):
            pygame.time.Clock().tick(3)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        t.rotate((field_width, field_height))
                    if event.key == pygame.K_s:
                        t.shift(Tetromino.down, field)
                    if event.key == pygame.K_a:
                        t.shift(Tetromino.left, field)
                    if event.key == pygame.K_d:
                        t.shift(Tetromino.right, field)
            draw_field(win, field, cell_size)
            t.draw(win, cell_size)
            pygame.display.update()
        field_append_tetromino(t, field)


if __name__ == '__main__':
    main()
