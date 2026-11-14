"""
Ball and paddle physics of the game, run by the server (see session.py).

Positions are in court pixels (the Phaser canvas is CANVAS_WIDTH x
CANVAS_HEIGHT) and speeds in pixels per second, so the game runs at the same
speed whatever the players' frame rates. Sizes match the sprites in
static/game/assets: the visible paddle is 20 x 124 px, the ball 30 px wide.

The ball bounces off the front face of a paddle (and off its top and bottom
ends), not off a line through its middle. The bounce angle depends on where
the ball meets the paddle: straight back from the middle, up to
MAX_BOUNCE_ANGLE near the ends, as in the classic game.
"""

import math
import random

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 640

PLAYER_LEFT = 0
PLAYER_RIGHT = 1

BALL_RADIUS = 15
PADDLE_HALF_WIDTH = 10
PADDLE_HALF_HEIGHT = 62
# Paddle centres: 10 px from each side, so they touch the court edges.
LEFT_PADDLE_X = 10
RIGHT_PADDLE_X = CANVAS_WIDTH - 10

PADDLE_SPEED = 480            # px/s when a player holds a key
BALL_START_SPEED = 360        # px/s at every serve
BALL_MAX_SPEED = 840          # px/s
BALL_SPEEDUP = 1.06           # speed factor on every paddle hit
MAX_BOUNCE_ANGLE = math.radians(60)
MAX_SERVE_ANGLE = math.radians(30)


class Paddle:
    def __init__(self, x):
        self.x = x
        self.y = CANVAS_HEIGHT / 2
        self.velocity = 0.0   # px/s, positive is down

    @property
    def top(self):
        return self.y - PADDLE_HALF_HEIGHT

    @property
    def bottom(self):
        return self.y + PADDLE_HALF_HEIGHT

    def move(self, dt):
        # The whole paddle stays on the court.
        self.y = min(max(self.y + self.velocity * dt, PADDLE_HALF_HEIGHT), CANVAS_HEIGHT - PADDLE_HALF_HEIGHT)


class Ball:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.serve(self.rng.choice((PLAYER_LEFT, PLAYER_RIGHT)))

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)

    def serve(self, towards):
        """Put the ball in the centre, moving towards ``towards`` at the start speed."""
        self.x = CANVAS_WIDTH / 2
        self.y = CANVAS_HEIGHT / 2
        angle = self.rng.uniform(-MAX_SERVE_ANGLE, MAX_SERVE_ANGLE)
        direction = -1 if towards == PLAYER_LEFT else 1
        self.vx = direction * BALL_START_SPEED * math.cos(angle)
        self.vy = BALL_START_SPEED * math.sin(angle)


def _bounce_off_paddle(ball, paddle, face_x, hit_y, direction):
    """Send the ball back from ``face_x``; ``direction`` is +1 (right) or -1 (left)."""
    offset = (hit_y - paddle.y) / (PADDLE_HALF_HEIGHT + BALL_RADIUS)
    angle = max(-1.0, min(1.0, offset)) * MAX_BOUNCE_ANGLE
    speed = min(ball.speed * BALL_SPEEDUP, BALL_MAX_SPEED)
    ball.vx = direction * speed * math.cos(angle)
    ball.vy = speed * math.sin(angle)
    ball.x = face_x
    ball.y = hit_y


def _crosses_face(x0, x1, y0, y1, face_x, paddle):
    """Where the ball centre crosses the plane ``face_x`` in front of ``paddle``
    during this step, if it does so within reach of the paddle (y), else None."""
    if (x0 - face_x) * (x1 - face_x) > 0 or x0 == x1:
        return None
    t = (x0 - face_x) / (x0 - x1)
    hit_y = y0 + (y1 - y0) * t
    if paddle.top - BALL_RADIUS <= hit_y <= paddle.bottom + BALL_RADIUS:
        return hit_y
    return None


def _push_out_of_paddle_end(ball, paddle):
    """The ball is beside a paddle's front face (it already went past it): if it
    touches the paddle's top or bottom end, bounce it away vertically."""
    if abs(ball.x - paddle.x) > PADDLE_HALF_WIDTH + BALL_RADIUS:
        return
    if paddle.top - BALL_RADIUS < ball.y < paddle.bottom + BALL_RADIUS:
        if ball.y < paddle.y:
            ball.y = paddle.top - BALL_RADIUS
            ball.vy = -abs(ball.vy)
        else:
            ball.y = paddle.bottom + BALL_RADIUS
            ball.vy = abs(ball.vy)


def step(ball, left, right, dt):
    """
    Advance paddles and ball by ``dt`` seconds.

    Returns PLAYER_LEFT / PLAYER_RIGHT when that player scored (the ball left
    the court on the other side), None otherwise.
    """
    left.move(dt)
    right.move(dt)

    x0, y0 = ball.x, ball.y
    x1, y1 = x0 + ball.vx * dt, y0 + ball.vy * dt

    # Top and bottom walls (the ball's edge bounces, not its centre).
    if y1 < BALL_RADIUS:
        y1 = 2 * BALL_RADIUS - y1
        ball.vy = abs(ball.vy)
    elif y1 > CANVAS_HEIGHT - BALL_RADIUS:
        y1 = 2 * (CANVAS_HEIGHT - BALL_RADIUS) - y1
        ball.vy = -abs(ball.vy)

    # Front faces of the paddles. The test is swept over the whole step, so a
    # fast ball cannot pass through a paddle between two steps.
    if ball.vx < 0:
        face_x = left.x + PADDLE_HALF_WIDTH + BALL_RADIUS
        hit_y = _crosses_face(x0, x1, y0, y1, face_x, left)
        if hit_y is not None:
            _bounce_off_paddle(ball, left, face_x, hit_y, +1)
            return None
    elif ball.vx > 0:
        face_x = right.x - PADDLE_HALF_WIDTH - BALL_RADIUS
        hit_y = _crosses_face(x0, x1, y0, y1, face_x, right)
        if hit_y is not None:
            _bounce_off_paddle(ball, right, face_x, hit_y, -1)
            return None

    ball.x, ball.y = x1, y1
    _push_out_of_paddle_end(ball, left)
    _push_out_of_paddle_end(ball, right)

    # A point once the ball has completely left the court.
    if ball.x - BALL_RADIUS > CANVAS_WIDTH:
        return PLAYER_LEFT
    if ball.x + BALL_RADIUS < 0:
        return PLAYER_RIGHT
    return None
