import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def return_mob(name, x, y, *group):
    if name == 'player':
        return Player(x, y, *group)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, *group):
        super().__init__(*group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Creature:
    def __init__(self, x, y, image, *group):
        self.x = x
        self.y = y
        self.im = AnimatedSprite(load_image(image), 8, 2, x, y, *group)

    def render(self):
        pass


class Player(Creature):
    def __init__(self, x, y, *group):
        super().__init__(x, y, image, *group)


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
        self.cells = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        with open(f"{file_name}.txt") as field:
            for i in range(y):
                line = field.readline().split()
                new_line = []
                for j in range(x):
                    new_line.append((line[j], None))
                    Cell(j * self.cell_size, i * cell_size, line[j], self.cells)
                self.field.append(new_line)
            mobs = field.readline().split('; ')
            for mob in mobs:
                mob = mob.split('_')
                x, y, name = int(mob[0]), int(mob[1]), mob[2]
                self.field[y][x] = (self.field[y][x][0], return_mob(name, x * cell_size, y * cell_size, self.mobs))

    def draw(self, screen):
        self.cells.draw(screen)
        self.mobs.update()
        self.mobs.draw(screen)
