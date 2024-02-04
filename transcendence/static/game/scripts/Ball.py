import random
from static.game.scripts.constants import *

class Ball:
    def __init__(self, initial_speed=2, max_speed=10, acceleration_interval=3000, acceleration_amount=0.1):
        self.initial_speed = initial_speed
        self.speed = self.initial_speed
        self.max_speed = max_speed
        self.acceleration_interval = acceleration_interval
        self.acceleration_amount = acceleration_amount
        self.set_acceleration_timer()
        self.set_directions()
        self.x = 0  # Adicione o valor inicial da posição X aqui
        self.y = 0  # Adicione o valor inicial da posição Y aqui
        self.velocity = self.set_random_direction()

    def hit_horizontal_borders(self, canvas_height):
        if self.y <= 0 or self.y >= canvas_height:
            self.velocity[1] *= -1

    def move(self):
        self.hit_horizontal_borders(CANVAS_HEIGHT)  # Certifique-se de substituir CANVAS_HEIGHT pelo valor apropriado
        self.y += self.velocity[1]
        self.x += self.velocity[0]

    def check_paddle_collision(self, x_paddle, y_paddle, paddle_height, player):
        offset = paddle_height / 2
        if player == PLAYER_LEFT:
            if x_paddle >= self.x >= x_paddle and y_paddle - offset <= self.y <= y_paddle + offset:
                self.velocity[0] *= -1
                self.last_hit_player = player
        else:
            if x_paddle <= self.x <= x_paddle and y_paddle - offset <= self.y <= y_paddle + offset:
                self.velocity[0] *= -1
                self.last_hit_player = player
        return [False, None]  # Certifique-se de adaptar o retorno conforme necessário

    def set_random_direction(self):
        return [random.uniform(-self.speed, self.speed), random.uniform(-self.speed, self.speed)]

    def accelerate_ball(self):
        self.speed += self.acceleration_amount

        if self.speed > self.max_speed:
            self.speed = self.max_speed

        self.velocity[0] += self.acceleration_amount if self.velocity[0] > 0 else -self.acceleration_amount
        self.velocity[1] += self.acceleration_amount if self.velocity[1] > 0 else -self.acceleration_amount

    def reset_ball(self, center_of_screen):
        self.x, self.y = center_of_screen  # Adicione o valor do centro da tela aqui
        self.speed = self.initial_speed
        self.set_directions()
        self.reset_acceleration_timer()
        self.velocity = self.set_random_direction()

    def set_directions(self):
        self.directions = [
            [self.speed, self.speed],
            [-self.speed, self.speed],
            [self.speed, -self.speed],
            [-self.speed, -self.speed],
        ]

    def reset_acceleration_timer(self):
        if hasattr(self, "acceleration_timer") and self.acceleration_timer:
            self.acceleration_timer.cancel()
        self.set_acceleration_timer()

    def set_acceleration_timer(self):
        # Implemente a lógica de temporizador apropriada para o ambiente Python
        pass
