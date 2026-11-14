import math
import random
from unittest import TestCase

from srcs_game.physics import (
    BALL_MAX_SPEED,
    BALL_RADIUS,
    BALL_START_SPEED,
    CANVAS_HEIGHT,
    LEFT_PADDLE_X,
    MAX_BOUNCE_ANGLE,
    PADDLE_HALF_HEIGHT,
    PADDLE_HALF_WIDTH,
    PLAYER_LEFT,
    PLAYER_RIGHT,
    RIGHT_PADDLE_X,
    Ball,
    Paddle,
    step,
)

DT = 1 / 60
# Where the ball centre is when its edge touches the front face of a paddle.
LEFT_FACE = LEFT_PADDLE_X + PADDLE_HALF_WIDTH + BALL_RADIUS    # 35
RIGHT_FACE = RIGHT_PADDLE_X - PADDLE_HALF_WIDTH - BALL_RADIUS  # 765


def ball(x, y, vx, vy):
    b = Ball(random.Random(0))
    b.x, b.y, b.vx, b.vy = x, y, vx, vy
    return b


def paddles(left_y=CANVAS_HEIGHT / 2, right_y=CANVAS_HEIGHT / 2):
    left, right = Paddle(LEFT_PADDLE_X), Paddle(RIGHT_PADDLE_X)
    left.y, right.y = left_y, right_y
    return left, right


def run(b, left, right, seconds, dt=DT):
    """Step until a point is scored or ``seconds`` pass; returns the scorer and
    the smallest x the ball centre reached."""
    min_x = b.x
    for _ in range(round(seconds / dt)):
        scorer = step(b, left, right, dt)
        min_x = min(min_x, b.x)
        if scorer is not None:
            return scorer, min_x
    return None, min_x


class PaddleCollisionTestCase(TestCase):
    def test_ball_bounces_off_the_paddle_border_not_its_centre(self):
        b = ball(200, 320, -BALL_START_SPEED, 0)
        left, right = paddles()

        scorer, min_x = run(b, left, right, 1.5)

        self.assertIsNone(scorer)
        self.assertGreater(b.vx, 0)
        # The ball edge touched the paddle's front face (x = 20): its centre never
        # went further than 35, far from the paddle's centre line (x = 10).
        self.assertAlmostEqual(min_x, LEFT_FACE)
        self.assertAlmostEqual(min_x - BALL_RADIUS, LEFT_PADDLE_X + PADDLE_HALF_WIDTH)

    def test_right_paddle_too(self):
        b = ball(600, 320, BALL_START_SPEED, 0)
        left, right = paddles()

        for _ in range(60):
            step(b, left, right, DT)
            self.assertLessEqual(b.x, RIGHT_FACE)

        self.assertLess(b.vx, 0)

    def test_centre_hit_goes_straight_back_edge_hit_goes_steep(self):
        centre = ball(LEFT_FACE + 5, 320, -300, 0)
        left, right = paddles(left_y=320)
        step(centre, left, right, DT)
        self.assertAlmostEqual(centre.vy, 0)

        edge = ball(LEFT_FACE + 5, 320 + PADDLE_HALF_HEIGHT, -300, 0)
        left, right = paddles(left_y=320)
        step(edge, left, right, DT)
        angle = math.atan2(edge.vy, edge.vx)
        self.assertGreater(edge.vy, 0)  # hit below the middle: goes down
        self.assertGreater(angle, MAX_BOUNCE_ANGLE * 0.7)

    def test_ball_just_beyond_the_paddle_end_is_missed(self):
        # Ball edge passes 1 px below the paddle's bottom.
        y = 320 + PADDLE_HALF_HEIGHT + BALL_RADIUS + 1
        b = ball(200, y, -BALL_START_SPEED, 0)
        left, right = paddles(left_y=320)

        scorer, _ = run(b, left, right, 2)

        self.assertEqual(scorer, PLAYER_RIGHT)
        self.assertLess(b.x + BALL_RADIUS, 0)  # only once the ball has fully left

    def test_ball_grazing_the_paddle_end_is_returned(self):
        y = 320 + PADDLE_HALF_HEIGHT + BALL_RADIUS - 1
        b = ball(200, y, -BALL_START_SPEED, 0)
        left, right = paddles(left_y=320)

        scorer, _ = run(b, left, right, 1.5)

        self.assertIsNone(scorer)
        self.assertGreater(b.vx, 0)

    def test_ball_hitting_the_top_of_a_paddle_bounces_up(self):
        # The ball is beside the paddle (already past its face) and falls on it.
        b = ball(LEFT_PADDLE_X, 320 - PADDLE_HALF_HEIGHT - BALL_RADIUS - 2, -10, 300)
        left, right = paddles(left_y=320)

        step(b, left, right, DT)

        self.assertLess(b.vy, 0)
        self.assertLessEqual(b.y, left.top - BALL_RADIUS)

    def test_fast_ball_cannot_pass_through_a_paddle(self):
        b = ball(LEFT_FACE + 30, 320, -BALL_MAX_SPEED, 0)
        left, right = paddles()

        step(b, left, right, 0.05)  # 42 px in one step, more than the paddle width

        self.assertGreater(b.vx, 0)
        self.assertAlmostEqual(b.x, LEFT_FACE)

    def test_every_hit_speeds_the_ball_up_to_a_maximum(self):
        b = ball(LEFT_FACE + 5, 320, -BALL_START_SPEED, 0)
        left, right = paddles()
        step(b, left, right, DT)
        self.assertAlmostEqual(b.speed, BALL_START_SPEED * 1.06)

        b = ball(LEFT_FACE + 5, 320, -BALL_MAX_SPEED, 0)
        step(b, left, right, DT)
        self.assertAlmostEqual(b.speed, BALL_MAX_SPEED)


class CourtTestCase(TestCase):
    def test_ball_edge_bounces_off_the_walls(self):
        b = ball(400, BALL_RADIUS + 2, 0, -300)
        left, right = paddles()

        step(b, left, right, DT)

        self.assertGreater(b.vy, 0)
        self.assertGreaterEqual(b.y, BALL_RADIUS)

    def test_paddles_stay_on_the_court(self):
        left, right = paddles()
        left.velocity, right.velocity = -10_000, 10_000
        left.move(1)
        right.move(1)
        self.assertEqual((left.top, right.bottom), (0, CANVAS_HEIGHT))

    def test_serve_goes_to_the_receiver_at_start_speed(self):
        b = Ball(random.Random(1))
        b.serve(PLAYER_LEFT)
        self.assertLess(b.vx, 0)
        self.assertAlmostEqual(b.speed, BALL_START_SPEED)
        self.assertEqual((b.x, b.y), (400, 320))
        b.serve(PLAYER_RIGHT)
        self.assertGreater(b.vx, 0)
