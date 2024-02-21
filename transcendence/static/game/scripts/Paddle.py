from static.game.scripts.constants import *
from static.game.scripts.Vector2 import Vector2

class Paddle:
    def __init__(self, x, y):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)

    def hit_horizontal_borders(self):        
        if self.position.y <= OFFSET:
            self.position.y = OFFSET
            self.velocity.y = 0
        elif self.position.y >= CANVAS_HEIGHT - OFFSET:
            self.position.y = CANVAS_HEIGHT - OFFSET
            self.velocity.y = 0

    async def move(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        self.hit_horizontal_borders()

    async def set_paddle_velocity(self, x, y):
        self.velocity.x = x
        self.velocity.y = y

    def reset_paddle(self, player):
        if player == PLAYER_LEFT:
            self.y = LEFT_PADDLE_START_POSITION.y
        else:
            self.y = RIGHT_PADDLE_START_POSITION.y

    def position_to_dict(self):
        return {'x': self.position.x, 'y': self.position.y}
