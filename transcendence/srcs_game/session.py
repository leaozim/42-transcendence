"""
In-memory state of a game being played, advanced by the server's game loop
(see consumers.run_game) and fed with the players' input by the consumer.

Lifecycle of a game:

    WAITING    players join the game room and press "Ready"
    COUNTDOWN  both players are in the room and ready; play begins after
               COUNTDOWN_SECONDS
    PLAYING    the ball moves and the clock runs
    FINISHED   the time is up or a player reached the target score,
               whichever happens first

The clock starts when play begins, not when the game is created. The ball
moves in real time (see physics.py), independently of the clients' frame
rates; clients only send their paddle direction when it changes. Time is
passed in explicitly (``now``, ``dt``), which keeps this class easy to test.
"""

import math
import random
from collections import Counter

from srcs_game.physics import (
    LEFT_PADDLE_X,
    PADDLE_SPEED,
    PLAYER_LEFT,
    PLAYER_RIGHT,
    RIGHT_PADDLE_X,
    Ball,
    Paddle,
    step,
)

WAITING = "waiting"
COUNTDOWN = "countdown"
PLAYING = "playing"
FINISHED = "finished"

COUNTDOWN_SECONDS = 3
# After a point the ball waits this long in the centre before it is served.
SERVE_DELAY = 1.0


class GameSession:
    def __init__(self, left_player_id, right_player_id, duration_seconds, target_score=None, computer=None, rng=None):
        self.players = (left_player_id, right_player_id)
        self.duration = duration_seconds
        self.target_score = target_score
        self.computer = computer
        self.ball = Ball(rng or random.Random())
        self.left_paddle = Paddle(LEFT_PADDLE_X)
        self.right_paddle = Paddle(RIGHT_PADDLE_X)
        self.score = [0, 0]
        self.connections = Counter()  # open connections of each player
        self.sockets = 0              # all open connections, spectators included
        self.ready = set()
        self.phase = WAITING
        self.play_starts_at = None
        self.serve_at = None
        self.finished_at = None
        self.finish_reason = None
        # Something other than the ball moved (players, ready, phase): the game
        # loop broadcasts the state even outside play.
        self.changed = True
        if computer is not None:
            # The computer is always in the room and always ready.
            self.connections[right_player_id] += 1
            self.ready.add(right_player_id)

    # --- players -------------------------------------------------------------

    def side(self, user_id):
        """PLAYER_LEFT / PLAYER_RIGHT for a player, None for spectators."""
        return self.players.index(user_id) if user_id in self.players else None

    def paddle(self, side):
        return self.left_paddle if side == PLAYER_LEFT else self.right_paddle

    def is_connected(self, user_id):
        return self.connections[user_id] > 0

    @property
    def humans_present(self):
        """Is any (human) player in the room? The computer does not count."""
        humans = self.players[:1] if self.computer is not None else self.players
        return any(self.is_connected(p) for p in humans)

    def connect(self, user_id):
        self.sockets += 1
        self.changed = True
        if self.side(user_id) is not None:
            self.connections[user_id] += 1

    def disconnect(self, user_id):
        self.sockets = max(0, self.sockets - 1)
        self.changed = True
        side = self.side(user_id)
        if side is None or self.connections[user_id] == 0:
            return
        self.connections[user_id] -= 1
        if self.connections[user_id] == 0:
            self.paddle(side).velocity = 0.0
            if self.phase in (WAITING, COUNTDOWN):
                # Leaving before play starts withdraws "Ready" and stops the countdown.
                self.ready.discard(user_id)
                self.phase = WAITING
                self.play_starts_at = None

    def set_ready(self, user_id, now):
        if self.phase != WAITING or self.side(user_id) is None or not self.is_connected(user_id):
            return False
        self.ready.add(user_id)
        self.changed = True
        if all(self.is_connected(p) and p in self.ready for p in self.players):
            self.phase = COUNTDOWN
            self.play_starts_at = now + COUNTDOWN_SECONDS
        return True

    def set_direction(self, user_id, direction):
        """A player holds up (-1), down (+1) or no key (0)."""
        side = self.side(user_id)
        if side is None or (self.computer is not None and side == PLAYER_RIGHT):
            return
        direction = max(-1, min(1, int(direction)))
        self.paddle(side).velocity = direction * PADDLE_SPEED

    # --- game loop -----------------------------------------------------------

    def update(self, now, dt):
        """Advance the game by ``dt`` seconds. Returns True when play just began."""
        started = False
        if self.phase == COUNTDOWN and now >= self.play_starts_at:
            self.phase = PLAYING
            self.changed = True
            started = True
        if self.phase != PLAYING:
            return started
        if now >= self.play_starts_at + self.duration:
            self.finish("time", self.play_starts_at + self.duration)
            return started

        if not self.humans_present:
            # Everybody left: nothing moves (and nobody scores) while the clock
            # runs out; the game then ends with the score they left it at.
            return started

        if self.computer is not None:
            self.right_paddle.velocity = self.computer.velocity_y(self.ball, self.right_paddle)

        if self.serve_at is not None and now < self.serve_at:
            # Between points: the ball waits in the centre, the paddles can move.
            self.left_paddle.move(dt)
            self.right_paddle.move(dt)
            return started
        self.serve_at = None

        scorer = step(self.ball, self.left_paddle, self.right_paddle, dt)
        if scorer is not None:
            self.score[scorer] += 1
            self.changed = True
            if self.target_score and self.score[scorer] >= self.target_score:
                self.finish("score", now)
            else:
                # The player who lost the point receives the next ball.
                self.ball.serve(towards=1 - scorer)
                self.serve_at = now + SERVE_DELAY
        return started

    def time_left(self, now):
        if self.phase in (WAITING, COUNTDOWN):
            return self.duration
        end = self.finished_at if self.phase == FINISHED else now
        return max(0.0, self.play_starts_at + self.duration - end)

    def finish(self, reason, now):
        self.phase = FINISHED
        self.finish_reason = reason
        self.finished_at = now
        self.changed = True

    @property
    def winner_side(self):
        if self.score[PLAYER_LEFT] == self.score[PLAYER_RIGHT]:
            return None
        return PLAYER_LEFT if self.score[PLAYER_LEFT] > self.score[PLAYER_RIGHT] else PLAYER_RIGHT

    # --- state sent to the clients -------------------------------------------

    def state(self, now):
        data = {
            "phase": self.phase,
            "ball_x": round(self.ball.x, 1),
            "ball_y": round(self.ball.y, 1),
            "left_player_position_x": self.left_paddle.x,
            "left_player_position_y": round(self.left_paddle.y, 1),
            "right_player_position_x": self.right_paddle.x,
            "right_player_position_y": round(self.right_paddle.y, 1),
            "score": list(self.score),
            "connected": [p for p in self.players if self.is_connected(p)],
            "ready": [p for p in self.players if p in self.ready],
            "duration": self.duration,
            "target_score": self.target_score,
            "time_left": round(self.time_left(now), 2),
            "countdown": None,
        }
        if self.phase == COUNTDOWN:
            data["countdown"] = max(1, math.ceil(self.play_starts_at - now))
        if self.phase == FINISHED:
            side = self.winner_side
            data["result"] = "draw" if side is None else "win"
            data["winner_id"] = None if side is None else self.players[side]
            data["finish_reason"] = self.finish_reason
        return data
