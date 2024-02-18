import random
from static.game.scripts.constants import *
from static.game.scripts.Vector2 import Vector2

class Ball:
    def __init__(self, initial_speed=2, max_speed=10, acceleration_interval=3000, acceleration_amount=0.1):
        self.initial_speed = initial_speed
        self.speed = self.initial_speed
        self.max_speed = max_speed
        self.acceleration_interval = acceleration_interval
        self.acceleration_amount = acceleration_amount
        # self.set_acceleration_timer()
        self.set_directions()
        self.position = Vector2(CENTER_OF_SCREEN.x, CENTER_OF_SCREEN.y)
        self.velocity = self.set_random_direction()

    def hit_horizontal_borders(self, canvas_height):
        if self.position.y <= 0 or self.position.y >= canvas_height:
            self.velocity.y *= -1

    async def move(self):
        self.hit_horizontal_borders(CANVAS_HEIGHT)
        if self.position.x <= 0 or self.position.x >= CANVAS_WIDTH:
            self.velocity.x *= -1
        self.position.y += self.velocity.y
        self.position.x += self.velocity.x

    def check_paddle_collision(self, x_paddle, y_paddle, paddle_height, player):
        offset = paddle_height / 2
        if player == PLAYER_LEFT:
            if x_paddle >= self.position.x >= x_paddle and y_paddle - offset <= self.position.y <= y_paddle + offset:
                self.velocity.x *= -1
                self.last_hit_player = player
        else:
            if x_paddle <= self.position.x <= x_paddle and y_paddle - offset <= self.position.y <= y_paddle + offset:
                self.velocity.x *= -1
                self.last_hit_player = player
        return [False, None]  # Certifique-se de adaptar o retorno conforme necessário

    def set_random_direction(self):
        return Vector2(1, 1)

    def accelerate_ball(self):
        self.speed += self.acceleration_amount

        if self.speed > self.max_speed:
            self.speed = self.max_speed

        self.velocity.x += self.acceleration_amount if self.velocity.x > 0 else -self.acceleration_amount
        self.velocity.y += self.acceleration_amount if self.velocity.y > 0 else -self.acceleration_amount

    def reset_ball(self, center_of_screen):
        self.position.x, self.position.y = center_of_screen
        self.speed = self.initial_speed
        self.set_directions()
        self.reset_acceleration_timer()
        self.velocity = self.set_random_direction()

    def set_directions(self):
        self.directions = [
            Vector2(self.speed, self.speed),
            Vector2(-self.speed, self.speed),
            Vector2(self.speed, -self.speed),
            Vector2(-self.speed, -self.speed),
        ]

    def reset_acceleration_timer(self):
        # Implemente a lógica de temporizador apropriada para o ambiente Python
        pass
