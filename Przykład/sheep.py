import random


class Sheep:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dist = 0.0
        self.status = "alive"
        self.no = 0

    def move(self, sheep_move_dist):
        direction = random.randint(1, 4)
        if direction == 1:
            self.y += sheep_move_dist
        elif direction == 2:
            self.x += sheep_move_dist
        elif direction == 3:
            self.y -= sheep_move_dist
        else:
            self.x -= sheep_move_dist
