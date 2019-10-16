import pygame
import math


# math constants
cos60 = 0.5
sin60 = math.sin(math.radians(60))


class Block:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def get_vertices(self):
        coords = ((0, sin60, 0), (cos60, 0, 0), (1 + cos60, 0, 0), (2, sin60, 0),
                  (1 + cos60, 2 * sin60, 0), (cos60, 2 * sin60, 0), (0, sin60, 1), (cos60, 0, 1),
                  (1 + cos60, 0, 1), (2, sin60, 1), (1 + cos60, 2 * sin60, 1), (cos60, 2 * sin60, 1))
        if self.x % 2 == 1:
            for vert in coords:
                vert[1] += sin60
        result = []
        for ex_x, ex_y, ex_z in coords:
            result.append((ex_x + (self.x / 2 * 3), ex_y + (self.y * 2 * sin60), self.z + ex_z))
        return result


def main():
    pygame.init()
    pygame_app = True
    while pygame_app:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    ''
            if event.type == pygame.MOUSEMOTION:
                print(pygame.mouse.get_rel())


if __name__ == '__main__':
    main()
