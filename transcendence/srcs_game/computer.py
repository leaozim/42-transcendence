"""
Computer opponent for single-player games.

A game against the computer is a regular Game whose right player is the bot
user (the same account that greets new users in the chat). The game loop
moves the right paddle with ComputerPlayer instead of a second client.

The computer is beatable on purpose: it only reacts once the ball has crossed
the middle of the court towards it, its paddle is slower than a player's, and
it aims at the predicted impact point with a random error. When the error is
larger than the paddle can cover, it misses.
"""

import random

from srcs_game.physics import (
    BALL_RADIUS,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    PADDLE_HALF_WIDTH,
)

# Top paddle speed in px/s (a player's paddle moves at PADDLE_SPEED, 480 px/s).
COMPUTER_SPEED = 340
# Slower drift back to the centre while the ball is moving away.
COMPUTER_RETURN_SPEED = 160
# The paddle speeds up in proportion to the distance left (1/s), which keeps
# it from jittering around its target.
STEERING_GAIN = 8
# The computer starts tracking the ball once it crosses this x (heading right).
REACTION_X = CANVAS_WIDTH * 0.45
# Maximum aiming error in pixels, drawn once per incoming ball. The paddle
# reaches the ball when the error is below about 77 px (half the paddle plus
# the ball's radius). In simulated 1-minute games the computer returns about
# 80% of the balls: a careful player (who anticipates the bounces) nearly
# always wins; a casual one (who follows the ball) wins about 60% of the
# games, draws 15% and loses 25%.
MAX_AIM_ERROR = 100
DEAD_ZONE = 2


def computer_player_id():
    """User id of the computer opponent (the chat bot, created at start-up)."""
    from srcs_message.services import BOT_ID

    return BOT_ID


def predict_ball_y(ball, target_x):
    """Where the ball centre will cross ``target_x``, following wall bounces."""
    if ball.vx == 0:
        return ball.y
    seconds = (target_x - ball.x) / ball.vx
    if seconds < 0:
        return ball.y
    span = CANVAS_HEIGHT - 2 * BALL_RADIUS
    y = (ball.y - BALL_RADIUS + ball.vy * seconds) % (2 * span)
    return BALL_RADIUS + (2 * span - y if y > span else y)


class ComputerPlayer:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.aim_error = None
        self.last_ball_x = None

    def velocity_y(self, ball, paddle):
        """Vertical paddle speed (px/s) for the next step."""
        incoming = ball.vx > 0 and ball.x >= REACTION_X
        # After a point the ball restarts from the centre, possibly still heading
        # here: that is a new ball, so aim afresh.
        new_ball = self.last_ball_x is not None and ball.x < self.last_ball_x and ball.vx > 0
        self.last_ball_x = ball.x
        if incoming:
            if self.aim_error is None or new_ball:
                self.aim_error = self.rng.uniform(-MAX_AIM_ERROR, MAX_AIM_ERROR)
            face_x = paddle.x - PADDLE_HALF_WIDTH - BALL_RADIUS
            target = predict_ball_y(ball, face_x) + self.aim_error
            speed = COMPUTER_SPEED
        else:
            self.aim_error = None
            target = CANVAS_HEIGHT / 2
            speed = COMPUTER_RETURN_SPEED

        difference = target - paddle.y
        if abs(difference) <= DEAD_ZONE:
            return 0.0
        return max(-speed, min(speed, difference * STEERING_GAIN))
