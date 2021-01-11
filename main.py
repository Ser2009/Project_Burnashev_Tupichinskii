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
    if name == 'fire':
        return Fire(x, y, *group)


def game_over(level_number):
    background = load_image('game_over.png')
    buts_over = []
    buts_over.append(Button(256, 470, 200, 100, 'restart'))
    buts_over.append(Button(768, 470, 200, 100, 'menu'))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for but in buts_over:
                    if but.get_coords(event.pos[0], event.pos[1]) == 'menu':
                        running = False
                    if but.get_coords(event.pos[0], event.pos[1]) == 'restart':
                        running = False
                        level(level_number, screen)
        screen.blit(background, (0, 0))
        for but in buts_over:
            but.render(screen)
        pygame.display.flip()


def win():
    background = load_image('you_win.png')
    buts_over = []
    buts_over.append(Button(540, 470, 200, 100, 'menu'))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                for but in buts_over:
                    if but.get_coords(event.pos[0], event.pos[1]) == 'menu':
                        running = False
        screen.blit(background, (0, 0))
        for but in buts_over:
            but.render(screen)
        pygame.display.flip()


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
    def __init__(self, x, y, col, row, image, *group):
        self.x = x
        self.y = y
        self.im = AnimatedSprite(load_image(image), col, row, x, y, *group)

    def render(self):
        pass


class Player(Creature):
    def __init__(self, x, y, *group):
        image = 'player.png'
        super().__init__(x, y, 8, 1, image, *group)
        self.health = 10
        self.in_fire = False


class Fire(Creature):
    def __init__(self, x, y, *group):
        image = 'fire.png'
        super().__init__(x, y, 3, 2, image, *group)


class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, im_name, *group):
        super().__init__(*group)
        self.image = load_image(f"{im_name}.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = im_name


class Star(pygame.sprite.Sprite):
    def __init__(self, x, y, *group):
        super().__init__(*group)
        self.image = load_image("star.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Field:
    def __init__(self, file_name, x, y, cell_size):
        self.opened = False
        self.count = 0
        self.field = []
        self.file_name = file_name
        self.x, self.y = x, y
        self.cell_size = cell_size
        self.cells = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        with open(f"{file_name}.txt") as field:
            for i in range(y):
                line = field.readline().split()
                new_line = []
                for j in range(x):
                    if line[j] == 'trapdoor':
                        self.door = j, i
                    new_line.append((line[j], None))
                    Cell(j * self.cell_size, i * cell_size, line[j], self.cells)
                self.field.append(new_line)
            mobs = field.readline().split('; ')
            if mobs[0]:
                for mob in mobs:
                    mob = mob.split('_')
                    x, y, name = int(mob[0]), int(mob[1]), mob[2]
                    if name == 'player':
                        self.pl_coords = (x, y)
                        pl = return_mob(name, x * cell_size, y * cell_size)
                        self.pl_sprite = pl.im
                        self.mobs.add(self.pl_sprite)
                        self.field[y][x] = (self.field[y][x][0], pl)
                    else:
                        self.field[y][x] = (self.field[y][x][0], return_mob(name, x * cell_size, y * cell_size,
                                                                            self.mobs))
            stars = field.readline().split('; ')
            for star in stars:
                star = star.split('_')
                x, y = int(star[0]), int(star[1])
                self.field[y][x] = (self.field[y][x][0], Star(x * cell_size, y * cell_size, self.stars))

    def draw(self, screen):
        self.cells.draw(screen)
        self.stars.draw(screen)
        self.mobs.update()
        self.mobs.draw(screen)

    def move(self, x, y):
        x_0, y_0 = self.pl_coords
        x_1, y_1 = x_0 + x, y_0 + y
        if 0 <= x_1 < self.x and 0 <= y_1 < self.y:
            if self.field[y_1][x_1][0] == 'wall':
                return True
            if type(self.field[y_1][x_1][1]) == Star:
                self.count += 1
                self.field[y_1][x_1][1].kill()
            self.pl_coords = x_1, y_1
            cell, pl = self.field[y_0][x_0]
            self.field[y_0][x_0] = cell, None
            if pl.in_fire:
                self.field[y_0][x_0] = cell, Fire(x_0, y_0)
            if self.is_fire(x_1, y_1):
                pl.health -= 1
                pl.in_fire = True
            else:
                pl.in_fire = False
            self.field[y_1][x_1] = self.field[y_1][x_1][0], pl
            self.pl_sprite.rect = self.pl_sprite.rect.move(x * self.cell_size, y * self.cell_size)
            if pl.health == 0:
                game_over(self.file_name)
                return False
            if self.count == 5 and not self.opened:
                self.open()
            if self.opened and self.door == (x_1, y_1):
                win()
                return False
        return True

    def is_fire(self, x, y):
        if type(self.field[y][x][1]) == Fire:
            return True
        return False

    def open(self):
        x, y = self.door
        Cell(x * self.cell_size, y * self.cell_size, 'blm', self.cells)
        self.opened = True


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
            if self.text == 'menu':
                return 'menu'
            if self.text == 'restart':
                return 'restart'
            self.clicked()

    def clicked(self):
            level(self.text, screen)


def level(name, screen):
    game = Field(name, 16, 9, 80)
    clock = pygame.time.Clock()
    fps = 24
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    alive = game.move(0, -1)
                elif event.key == pygame.K_s:
                    alive = game.move(0, 1)
                elif event.key == pygame.K_a:
                    alive = game.move(-1, 0)
                elif event.key == pygame.K_d:
                    alive = game.move(1, 0)
                else:
                    alive = True
                if not alive:
                    run = False
        game.draw(screen)
        clock.tick(fps)
        pygame.display.flip()
    running = False


if __name__ == '__main__':
    background = load_image('new_game.png')
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                    running = False
        try:
            screen.blit(background, (0, 0))
            pygame.display.flip()
        except:
            pass
    background = load_image('start.png')
    try:
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
    except:
        pass
    pygame.quit()
