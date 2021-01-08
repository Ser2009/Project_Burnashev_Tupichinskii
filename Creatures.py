class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Player(Creature):
    def __init__(self, x, y):
        super().__init__(x, y)
