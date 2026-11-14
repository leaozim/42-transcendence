import random
from unittest import TestCase

from srcs_game.computer import ComputerPlayer
from srcs_game.physics import BALL_RADIUS, BALL_START_SPEED, CANVAS_WIDTH, PADDLE_SPEED
from srcs_game.session import (
    COUNTDOWN,
    COUNTDOWN_SECONDS,
    FINISHED,
    PLAYING,
    SERVE_DELAY,
    WAITING,
    GameSession,
)

ALICE, BOB, CAROL = 10, 20, 30
DT = 1 / 60


def new_session(duration=60, target_score=None, computer=None):
    return GameSession(ALICE, BOB, duration, target_score, computer, rng=random.Random(4))


def start(session, now=0):
    """Both players join and press Ready at ``now``; returns when play begins."""
    for player in session.players:
        session.connect(player)
        session.set_ready(player, now)
    return now + COUNTDOWN_SECONDS


def run(session, start_time, seconds, dt=DT):
    """Advance the game loop for ``seconds``; returns the time reached."""
    now = start_time
    for _ in range(round(seconds / dt)):
        now += dt
        session.update(now, dt)
    return now


class LifecycleTestCase(TestCase):
    def test_clock_does_not_run_before_both_players_are_ready(self):
        session = new_session(duration=60)
        session.connect(ALICE)

        run(session, 0, 5)
        session.update(600, DT)  # ten minutes after creation

        self.assertEqual(session.phase, WAITING)
        self.assertEqual(session.state(600)["time_left"], 60)
        self.assertEqual((session.ball.x, session.ball.y), (400, 320))

    def test_ready_needs_both_players_in_the_room(self):
        session = new_session()
        session.connect(ALICE)
        session.set_ready(ALICE, 0)
        self.assertEqual(session.phase, WAITING)
        self.assertEqual(session.state(0)["ready"], [ALICE])

        session.connect(BOB)
        self.assertEqual(session.phase, WAITING)
        session.set_ready(BOB, 5)

        self.assertEqual(session.phase, COUNTDOWN)
        self.assertEqual(session.state(5)["countdown"], COUNTDOWN_SECONDS)

    def test_only_players_in_the_room_can_be_ready(self):
        session = new_session()
        session.connect(CAROL)  # spectator
        self.assertFalse(session.set_ready(CAROL, 0))
        self.assertFalse(session.set_ready(ALICE, 0))  # not connected
        self.assertEqual(session.state(0)["connected"], [])

    def test_countdown_then_play(self):
        session = new_session()
        begins = start(session, now=100)

        self.assertFalse(session.update(begins - 0.5, DT))
        self.assertEqual(session.phase, COUNTDOWN)
        self.assertEqual(session.state(begins - 0.5)["countdown"], 1)
        self.assertEqual(session.ball.x, 400)

        self.assertTrue(session.update(begins, DT))  # play just began
        self.assertEqual(session.phase, PLAYING)
        self.assertNotEqual(session.ball.x, 400)
        self.assertEqual(session.state(begins + 10)["time_left"], 50)

    def test_leaving_before_play_withdraws_ready(self):
        session = new_session()
        start(session)
        self.assertEqual(session.phase, COUNTDOWN)

        session.disconnect(BOB)

        self.assertEqual(session.phase, WAITING)
        self.assertEqual(session.state(1)["ready"], [ALICE])

    def test_time_limit_ends_the_game_even_if_nobody_sends_anything(self):
        session = new_session(duration=60)
        begins = start(session)
        session.update(begins, DT)
        session.score[:] = [2, 1]

        session.update(begins + 59.9, DT)
        self.assertEqual(session.phase, PLAYING)
        session.update(begins + 60, DT)

        state = session.state(begins + 61)
        self.assertEqual(session.phase, FINISHED)
        self.assertEqual((state["result"], state["winner_id"], state["finish_reason"]), ("win", ALICE, "time"))
        self.assertEqual(state["time_left"], 0)

    def test_draw_when_time_is_up_with_equal_scores(self):
        session = new_session(duration=60)
        begins = start(session)

        session.update(begins + 61, DT)

        state = session.state(begins + 61)
        self.assertEqual((state["result"], state["winner_id"]), ("draw", None))

    def test_score_limit_ends_the_game_before_the_time(self):
        session = new_session(duration=600, target_score=2)
        begins = start(session)
        session.update(begins, DT)
        session.score[:] = [1, 0]
        session.ball.x, session.ball.vx = CANVAS_WIDTH + BALL_RADIUS, 300  # right player missed

        session.update(begins + 5, DT)

        state = session.state(begins + 5)
        self.assertEqual(session.score, [2, 0])
        self.assertEqual((state["result"], state["winner_id"], state["finish_reason"]), ("win", ALICE, "score"))
        self.assertEqual(state["time_left"], 595)


class PlayTestCase(TestCase):
    def test_ball_moves_in_real_time_whatever_the_tick_rate(self):
        positions = []
        for dt in (1 / 30, 1 / 120):
            session = new_session()
            begins = start(session)
            session.update(begins, 0)
            run(session, begins, 0.5, dt)
            positions.append((round(session.ball.x, 3), round(session.ball.y, 3)))

        self.assertEqual(positions[0], positions[1])
        travelled = abs(positions[0][0] - 400) ** 2 + abs(positions[0][1] - 320) ** 2
        self.assertAlmostEqual(travelled ** 0.5, BALL_START_SPEED * 0.5, delta=1)

    def test_players_move_only_their_own_paddle(self):
        session = new_session()
        begins = start(session)
        session.connect(CAROL)

        session.set_direction(BOB, 1)
        session.set_direction(CAROL, -1)  # spectator: ignored
        run(session, begins, 0.25)

        self.assertAlmostEqual(session.right_paddle.y, 320 + PADDLE_SPEED * 0.25, delta=1)
        self.assertEqual(session.left_paddle.y, 320)

        session.set_direction(BOB, 0)
        y = session.right_paddle.y
        run(session, begins + 0.25, 0.25)
        self.assertEqual(session.right_paddle.y, y)

    def test_leaving_during_play_stops_the_paddle(self):
        session = new_session()
        begins = start(session)
        session.update(begins, DT)
        session.set_direction(ALICE, 1)

        session.disconnect(ALICE)

        self.assertEqual(session.left_paddle.velocity, 0)
        self.assertEqual(session.phase, PLAYING)

    def test_nothing_moves_while_everybody_is_away(self):
        session = new_session(duration=60)
        begins = start(session)
        now = run(session, begins, 1)
        session.score[:] = [1, 0]
        for player in session.players:
            session.disconnect(player)
        ball = (session.ball.x, session.ball.y)

        now = run(session, now, 5)
        self.assertEqual((session.ball.x, session.ball.y), ball)

        session.update(begins + 60, DT)  # the clock kept running
        self.assertEqual(session.phase, FINISHED)
        self.assertEqual(session.score, [1, 0])

    def test_play_goes_on_when_only_one_player_leaves(self):
        session = new_session()
        begins = start(session)
        session.update(begins, DT)
        session.disconnect(BOB)
        x = session.ball.x

        run(session, begins, 0.5)

        self.assertEqual(session.phase, PLAYING)

        self.assertNotEqual(session.ball.x, x)

    def test_after_a_point_the_ball_waits_then_goes_to_the_receiver(self):
        session = new_session()
        begins = start(session)
        session.update(begins, DT)
        session.ball.x, session.ball.vx = -BALL_RADIUS - 1, -300  # left player missed

        session.update(begins + 1, DT)
        self.assertEqual(session.score, [0, 1])
        self.assertEqual((session.ball.x, session.ball.y), (400, 320))
        self.assertLess(session.ball.vx, 0)  # served to the player who lost the point

        session.update(begins + 1 + SERVE_DELAY / 2, DT)
        self.assertEqual(session.ball.x, 400)  # still waiting
        session.update(begins + 1 + SERVE_DELAY, DT)
        self.assertLess(session.ball.x, 400)

    def test_computer_is_always_ready_and_steers_its_own_paddle(self):
        session = new_session(computer=ComputerPlayer(random.Random(1)))
        session.connect(ALICE)
        self.assertEqual(session.state(0)["connected"], [ALICE, BOB])

        session.set_ready(ALICE, 0)
        self.assertEqual(session.phase, COUNTDOWN)

        session.set_direction(BOB, 1)  # nobody can steer the computer
        self.assertEqual(session.right_paddle.velocity, 0)
        run(session, COUNTDOWN_SECONDS, 3)
        self.assertEqual(session.phase, PLAYING)
        self.assertNotEqual(session.ball.x, 400)
