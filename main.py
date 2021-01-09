import pygame
import os
import sys

pygame.init()
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)


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
        image = load_image()
        super().__init__(x, y, image, *group)
        self.health = 10
        self.in_fire = False


class Fire(Creature):
    def __init__(self, x, y, *group):
        image = load_image()
        super().__init__(x, y, image, *group)


class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, im_name, *group):
        super().__init__(*group)
        self.image = load_image(f"{im_name}.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = im_name


class Field:
    def __init__(self, file_name, x, y, cell_size):
        self.field = []
        self.x, self.y = x, y
        self.cell_size = cell_size
        self.cells = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        with open(f"{file_name}.txt") as field:
            print('hello!')
            for i in range(y):
                print('hello!')
                line = field.readline().split()
                new_line = []
                for j in range(x):
                    new_line.append((line[j], None))
                    print('hello!')
                    Cell(j * self.cell_size, i * cell_size, line[j], self.cells)
                self.field.append(new_line)
            mobs = field.readline().split('; ')
            if mobs[0]:
                for mob in mobs:
                    mob = mob.split('_')
                    x, y, name = int(mob[0]), int(mob[1]), mob[2]
                    if name == 'player':
                        self.pl_coords = (x, y)
                    self.field[y][x] = (self.field[y][x][0], return_mob(name, x * cell_size, y * cell_size, self.mobs))

    def draw(self, screen):
        self.cells.draw(screen)
        self.mobs.update()
        self.mobs.draw(screen)

    def move(self, x, y):
        x_0, y_0 = self.pl_coords
        x_1, y_1 = x_0 + x, y_0 + y
        if 0 <= x_1 <= self.x and 0 <= y_1 <= self.y:
            if self.field[y_1][x_1][0].name == 'wall':
                return
            self.pl_coords = x_1, y_1
            cell, pl = self.field[y][x]
            self.field[y_0][x_0] = cell, None
            if self.is_fire(x_1, y_1):
                pl.health -= 1
                pl.in_fire = True
            else:
                pl.in_fire = False
            self.field[y_1][x_1] = self.field[y_1][x_1][0], pl

    def is_fire(self, x, y):
        if type(self.field[y][x][1]) == Fire:
            return True
        return False


class Button:
    def __init__(self, x, y, w, h, text):
        self.x, self.y, self.w, self.h, self.text = x, y, w, h, text

    def render(self, screen):
        screen.fill(pygame.Color(167, 2, 2), (self.x, self.y, self.w, self.h))
        font = pygame.font.Font(None, 50)
        text = font.render(self.text, True, (0, 0, 0))
        text_w = text.get_width()
        text_h = text.get_height()
        text_x = self.x + (self.w - text_w) // 2
        text_y = self.y + (self.h - text_h) // 2
        screen.blit(text, (text_x, text_y))

    def get_coords(self, x, y):
        if self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h:
            self.clicked()

    def clicked(self):
        level(self.text, screen)


def level(name, screen):
    game = Field(name, 16, 9, 80)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        game.draw(screen)
        pygame.display.flip()
    running = False


if __name__ == '__main__':

    background = load_image('start.png')
    screen.blit(background, (0, 0))
    buts = []
    for i in range(3):
        buts.append(Button(170 + i * (200 + 170), 310, 200, 100, str(i + 1)))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for but in buts:
                    but.get_coords(event.pos[0], event.pos[1])
        screen.blit(background, (0, 0))
        for but in buts:
            but.render(screen)
        pygame.display.flip()
    pygame.quit()
