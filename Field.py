import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, im_name, *group):
        super().__init__(*group)
        self.image = load_image(f"{im_name}.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Field:
    def __init__(self, file_name, x, y, cell_size):
        self.field = []
        self.x, self.y = x, y
        self.cell_size = cell_size
        self.sprites = pygame.sprite.Group()
        with open(f"{file_name}.txt") as field:
            for i in range(y):
                line = field.readline().split()
                new_line = []
                for j in range(x):
                    new_line.append((line[j], None))
                    Cell(j * self.cell_size, i * cell_size, line[j], self.sprites)
                self.field.append(new_line)
            mobs = field.readline().split('; ')
            for mob in mobs:
                mob = mob.split('_')
                x, y, name = int(mob[0]), int(mob[1]), mob[2]
                self.field[y][x] = (self.field[y][x][0], name)

    def draw(self, screen):
        self.sprites.draw(screen)



