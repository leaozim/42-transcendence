import asyncio
import random
from unittest import mock

from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from srcs_auth.jwt_token import generate_jwt_token
from srcs_core.routing import websocket_urlpatterns
from srcs_game import computer, consumers
from srcs_game.session import COUNTDOWN_SECONDS
from srcs_game.models import Game
from srcs_game.services import create_computer_game, create_game
from srcs_user.models import User
from srcs_game.physics import BALL_RADIUS, CANVAS_HEIGHT, PADDLE_HALF_WIDTH, PADDLE_SPEED, RIGHT_PADDLE_X, Ball, Paddle

MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


class FixedRandom(random.Random):
    """rng whose uniform() always returns ``value`` (the aiming error)."""

    def __init__(self, value):
        super().__init__(0)
        self.value = value

    def uniform(self, a, b):
        return self.value


def ball_at(x, y, vx, vy):
    ball = Ball(random.Random(0))
    ball.x, ball.y, ball.vx, ball.vy = x, y, vx, vy
    return ball


def right_paddle(y=CANVAS_HEIGHT / 2):
    paddle = Paddle(RIGHT_PADDLE_X)
    paddle.y = y
    return paddle


FACE_X = RIGHT_PADDLE_X - PADDLE_HALF_WIDTH - BALL_RADIUS  # where the computer meets the ball


def create_bot():
    # The computer opponent is the chat bot, user id 1 (created at start-up).
    return User.objects.create_user("pong (BOT)", "", None, id=computer.computer_player_id())


class ComputerPlayerTestCase(TestCase):
    def test_prediction_follows_wall_bounces(self):
        # 365 px right and 365 px down from y=320 hits the bottom wall (625) and comes back up.
        self.assertAlmostEqual(computer.predict_ball_y(ball_at(400, 320, 300, 300), 765), 2 * 625 - 685)
        self.assertAlmostEqual(computer.predict_ball_y(ball_at(700, 300, 300, -300), 765), 235)
        self.assertEqual(computer.predict_ball_y(ball_at(700, 300, -300, 300), 765), 300)  # moving away

    def test_tracks_incoming_ball_to_the_predicted_point(self):
        player = computer.ComputerPlayer(FixedRandom(0))
        ball = ball_at(500, 100, 300, 300)  # will reach the paddle at y = 365
        paddle = right_paddle(y=200)

        for _ in range(60):
            paddle.velocity = player.velocity_y(ball, paddle)
            self.assertLessEqual(abs(paddle.velocity), computer.COMPUTER_SPEED)
            paddle.move(1 / 60)

        self.assertAlmostEqual(paddle.y, 365, delta=computer.DEAD_ZONE)

    def test_returns_to_centre_when_ball_moves_away(self):
        player = computer.ComputerPlayer(FixedRandom(0))
        paddle = right_paddle(y=600)

        self.assertEqual(player.velocity_y(ball_at(700, 300, -300, 300), paddle), -computer.COMPUTER_RETURN_SPEED)

    def test_does_not_react_before_the_ball_crosses_midfield(self):
        player = computer.ComputerPlayer(FixedRandom(0))
        paddle = right_paddle()

        self.assertEqual(player.velocity_y(ball_at(100, 10, 300, -300), paddle), 0)

    def test_large_aim_error_misses(self):
        # Aiming further away than half the paddle plus the ball radius means a miss.
        player = computer.ComputerPlayer(FixedRandom(computer.MAX_AIM_ERROR))
        ball = ball_at(500, 320, 300, 0)
        paddle = right_paddle()
        for _ in range(60):
            paddle.velocity = player.velocity_y(ball, paddle)
            paddle.move(1 / 60)

        self.assertGreater(abs(paddle.y - 320), 62 + BALL_RADIUS)

    def test_new_ball_gets_a_new_aim(self):
        rng = mock.Mock(uniform=mock.Mock(side_effect=[10.0, -20.0]))
        player = computer.ComputerPlayer(rng)
        paddle = right_paddle()
        player.velocity_y(ball_at(600, 300, 300, 300), paddle)
        player.velocity_y(ball_at(605, 305, 300, 300), paddle)
        self.assertEqual(player.aim_error, 10.0)

        player.velocity_y(ball_at(400, 320, 300, 100), paddle)  # ball served again after a point

        self.assertEqual(player.aim_error, -20.0)


@mock.patch.object(Game, "start_connection_timer")
class ComputerGameViewsTestCase(TestCase):
    def setUp(self):
        self.bot = create_bot()
        self.user = User.objects.create_user("solo", "solo@example.com", "S0lo-password!")
        self.client.force_login(self.user, backend=MODEL_BACKEND)

    def test_service_creates_game_against_the_bot(self, _timer):
        game = create_computer_game(self.user)

        self.assertEqual((game.leftPlayer, game.rightPlayer), (self.user, self.bot))
        self.assertTrue(game.against_computer)
        self.assertEqual((game.duration_minutes, game.target_score), (1, None))
        other = User.objects.create_user("friend", "f@example.com", "Fr1end-password!")
        self.assertFalse(create_game(self.user, other).against_computer)

    def test_form_post_starts_game_and_redirects_to_it(self, _timer):
        response = self.client.post(reverse("srcs_game:computer"), {"minutes": "3", "score": "5"})

        game = Game.objects.get(leftPlayer=self.user)
        self.assertRedirects(response, reverse("srcs_game:room", args=[game.id]), fetch_redirect_response=False)
        self.assertTrue(game.against_computer)
        self.assertEqual((game.duration_minutes, game.target_score), (3, 5))

    def test_json_post_used_by_the_game_modal(self, _timer):
        response = self.client.post(reverse("srcs_game:computer"), {"minutes": "", "score": ""}, HTTP_ACCEPT="application/json")

        game = Game.objects.get(leftPlayer=self.user)
        self.assertEqual(response.json(), {"room_id": game.id})
        self.assertEqual((game.duration_minutes, game.target_score), (1, None))  # defaults

    def test_invalid_settings_are_rejected(self, _timer):
        response = self.client.post(reverse("srcs_game:computer"), {"minutes": "0", "score": "99"}, HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
        self.assertFalse(Game.objects.exists())

    def test_get_and_anonymous_are_rejected(self, _timer):
        self.assertEqual(self.client.get(reverse("srcs_game:computer")).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post(reverse("srcs_game:computer")).status_code, 302)
        self.assertFalse(Game.objects.exists())

    def test_room_page_for_computer_game(self, _timer):
        game = create_computer_game(self.user, duration_minutes=2, target_score=3)

        response = self.client.get(reverse("srcs_game:room", args=[game.id]))

        self.assertContains(response, "const VS_COMPUTER = true;")
        self.assertContains(response, 'id="play-again-form"')
        self.assertContains(response, '<input type="hidden" name="minutes" value="2">')
        self.assertContains(response, '<input type="hidden" name="score" value="3">')
        self.assertContains(response, 'id="ready-button"')
        self.assertContains(response, '<script id="game-texts" type="application/json">')
        texts = response.context["game_texts"]
        self.assertEqual((texts["leftPlayer"], texts["rightPlayer"]), ("solo", "Computer"))
        self.assertEqual(texts["settings"], "2 minutes · first to 3 points")

    def test_room_page_in_brazilian_portuguese(self, _timer):
        game = create_computer_game(self.user, duration_minutes=1, target_score=1)
        self.client.cookies["django_language"] = "pt-br"

        response = self.client.get(reverse("srcs_game:room", args=[game.id]))

        texts = response.context["game_texts"]
        self.assertEqual(texts["rightPlayer"], "Computador")
        self.assertEqual(texts["winner"], "%(name)s venceu!")
        self.assertEqual(texts["settings"], "1 minuto · vence quem fizer 1 ponto")
        self.assertEqual(texts["ready"], "Pronto")

    def test_two_player_room_page(self, _timer):
        other = User.objects.create_user("friend", "f@example.com", "Fr1end-password!")
        game = create_game(self.user, other)

        response = self.client.get(reverse("srcs_game:room", args=[game.id]))

        self.assertContains(response, "const VS_COMPUTER = false;")
        self.assertNotContains(response, 'id="play-again-form"')
        self.assertContains(response, 'id="cancel-game-button"')
        texts = response.context["game_texts"]
        self.assertEqual((texts["leftPlayer"], texts["rightPlayer"]), ("solo", "friend"))
        self.assertEqual(texts["settings"], "1 minute · no point limit")

    def test_game_modal_offers_settings_and_the_computer(self, _timer):
        response = self.client.get(reverse("srcs_game:index"))

        self.assertContains(response, f'action="{reverse("srcs_game:computer")}"')
        self.assertContains(response, 'name="minutes"')
        self.assertContains(response, 'value="1"')
        self.assertContains(response, 'name="score"')
        self.assertContains(response, "Play against the computer")
        self.assertContains(response, "No other players have signed up yet.")
        self.assertNotContains(response, "pong (BOT)")


@mock.patch.object(Game, "start_connection_timer")
class ChallengeTestCase(TestCase):
    def setUp(self):
        create_bot()
        self.alice = User.objects.create_user("alice", "a@example.com", "Al1ce-password!")
        self.bob = User.objects.create_user("bob", "b@example.com", "B0b-password!")
        self.client.force_login(self.alice, backend=MODEL_BACKEND)

    def test_challenge_with_settings(self, _timer):
        response = self.client.post(reverse("srcs_game:create_game", args=[self.bob.id]), {"minutes": "2", "score": "7"})

        game = Game.objects.get()
        self.assertEqual(response.json(), {"room_id": game.id})
        self.assertEqual((game.leftPlayer, game.rightPlayer), (self.alice, self.bob))
        self.assertEqual((game.duration_minutes, game.target_score), (2, 7))
        self.assertIsNone(game.started_at)

    def test_challenge_requires_post(self, _timer):
        response = self.client.get(reverse("srcs_game:create_game", args=[self.bob.id]))

        self.assertEqual(response.status_code, 405)
        self.assertFalse(Game.objects.exists())

    def test_challenge_validation(self, _timer):
        url = reverse("srcs_game:create_game", args=[self.bob.id])
        self.assertEqual(self.client.post(url, {"minutes": "11"}).status_code, 400)
        self.assertEqual(self.client.post(reverse("srcs_game:create_game", args=[999]), {}).status_code, 404)
        self.assertFalse(Game.objects.exists())


@mock.patch.object(consumers, "TICK_SECONDS", 0.001)
@mock.patch.object(Game, "start_connection_timer")
class GameConsumerTestCase(TransactionTestCase):
    """Drives the real WebSocket consumer and game loop. The game clock is
    mocked; the loop ticks every millisecond of real time."""

    def setUp(self):
        consumers.games.clear()
        self.bot = create_bot()
        self.human = User.objects.create_user("solo", "solo@example.com", "S0lo-password!")
        self.friend = User.objects.create_user("friend", "f@example.com", "Fr1end-password!")
        self.application = URLRouter(websocket_urlpatterns)
        self.clock = mock.Mock(return_value=1000.0)
        patcher = mock.patch("srcs_game.consumers.time.time", self.clock)
        patcher.start()
        self.addCleanup(patcher.stop)

    async def stop_game_loops(self):
        for session in list(consumers.games.values()):
            session.task.cancel()
        consumers.games.clear()
        await asyncio.sleep(0.01)

    async def connect(self, game, user=None, headers=None):
        communicator = WebsocketCommunicator(self.application, f"/ws/game/broadcast/{game.id}/", headers=headers or [])
        if user is not None:
            communicator.scope["user"] = user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def tick(self, seconds=0.0, steps=1):
        """Let the game loop run while the clock advances by ``seconds``."""
        for _ in range(steps):
            self.clock.return_value += seconds / steps
            await asyncio.sleep(0.005)

    async def latest(self, *communicators):
        """Drain pending messages (the loop keeps sending during play, so for a
        limited time); return the last state seen by the first communicator."""
        states = {}
        loop = asyncio.get_running_loop()
        for communicator in communicators:
            deadline = loop.time() + 0.1
            while loop.time() < deadline and not await communicator.receive_nothing(timeout=0.02):
                states.setdefault(communicator, []).append(await communicator.receive_json_from())
        return states.get(communicators[0], [None])[-1]

    async def send(self, communicator, **message):
        await communicator.send_json_to(message)
        await self.tick()

    async def computer_game(self, **settings):
        return await Game.objects.acreate(leftPlayer=self.human, rightPlayer=self.bot, leftPlayerScore=0, rightPlayerScore=0, **settings)

    async def two_player_game(self, **settings):
        return await Game.objects.acreate(leftPlayer=self.human, rightPlayer=self.friend, leftPlayerScore=0, rightPlayerScore=0, **settings)

    async def start_playing(self, *communicators):
        for communicator in communicators:
            await self.send(communicator, type="ready")
        await self.tick(COUNTDOWN_SECONDS)
        await self.tick()

    async def test_computer_game_runs_on_the_server(self, _timer):
        game = await self.computer_game()
        human = await self.connect(game, self.human)
        await self.tick()
        state = await self.latest(human)
        self.assertEqual((state["phase"], sorted(state["connected"])), ("waiting", sorted([self.human.id, self.bot.id])))

        await self.send(human, type="ready")
        state = await self.latest(human)
        self.assertEqual((state["phase"], state["countdown"]), ("countdown", COUNTDOWN_SECONDS))

        await self.tick(COUNTDOWN_SECONDS)
        await self.tick(1.0, steps=60)  # no message from the client at all
        state = await self.latest(human)
        self.assertEqual(state["phase"], "playing")
        self.assertNotEqual((state["ball_x"], state["ball_y"]), (400, 320))
        self.assertAlmostEqual(state["time_left"], 59, delta=0.1)
        await game.arefresh_from_db()
        self.assertIsNotNone(game.started_at)
        await human.disconnect()
        await self.stop_game_loops()

    async def test_arrow_keys_move_the_paddle(self, _timer):
        game = await self.two_player_game()
        left = await self.connect(game, self.human)
        right = await self.connect(game, self.friend)
        await self.start_playing(left, right)

        await self.send(left, type="input", direction=1)
        await self.tick(0.25, steps=15)
        await self.send(left, type="input", direction=0)
        await self.tick(0.25, steps=15)

        state = await self.latest(left, right)
        self.assertAlmostEqual(state["left_player_position_y"], 320 + PADDLE_SPEED * 0.25, delta=10)
        self.assertEqual(state["right_player_position_y"], 320)
        await left.disconnect()
        await right.disconnect()
        await self.stop_game_loops()

    async def test_client_cannot_steer_the_computer_paddle(self, _timer):
        game = await self.computer_game()
        human = await self.connect(game, self.human)
        await self.start_playing(human)
        session = consumers.games[consumers.group_name(game.id)]
        session.ball.vx = -abs(session.ball.vx)  # ball moving away: the computer stays put

        await self.send(human, type="frame", right_player_velocity={"x": 0, "y": 500})
        await self.tick(0.2, steps=10)

        self.assertLessEqual(abs(session.right_paddle.velocity), computer.COMPUTER_RETURN_SPEED)
        await human.disconnect()
        await self.stop_game_loops()

    async def test_two_player_game_waits_for_both_players_to_be_ready(self, _timer):
        game = await self.two_player_game()
        left = await self.connect(game, self.human)
        await self.send(left, type="ready")
        await self.tick(300, steps=5)  # the opponent joins five minutes later
        state = await self.latest(left)
        self.assertEqual((state["phase"], state["ready"], state["time_left"]), ("waiting", [self.human.id], 60))

        right = await self.connect(game, self.friend)
        await self.send(right, type="ready")
        self.assertEqual((await self.latest(left, right))["phase"], "countdown")
        await self.tick(COUNTDOWN_SECONDS)
        await self.tick(0.5, steps=30)
        state = await self.latest(left, right)
        self.assertEqual(state["phase"], "playing")
        self.assertNotEqual(state["ball_x"], 400)
        await left.disconnect()
        await right.disconnect()
        await self.stop_game_loops()

    async def play_until_the_end(self, game, score, seconds=61):
        human = await self.connect(game, self.human)
        await self.start_playing(human)
        consumers.games[consumers.group_name(game.id)].score[:] = score
        await self.tick(seconds)
        await self.tick()
        state = await self.latest(human)
        await human.disconnect()
        return state

    async def test_computer_wins_on_time(self, _timer):
        game = await self.computer_game()

        state = await self.play_until_the_end(game, [1, 2])

        self.assertEqual((state["phase"], state["result"], state["winner_id"]), ("finished", "win", self.bot.id))
        self.assertEqual(state["finish_reason"], "time")
        await game.arefresh_from_db()
        self.assertTrue(game.is_finish)
        self.assertEqual((game.winner_id, game.leftPlayerScore, game.rightPlayerScore), (self.bot.id, 1, 2))
        self.assertNotIn(consumers.group_name(game.id), consumers.games)

    async def test_human_wins_on_time(self, _timer):
        game = await self.computer_game()

        state = await self.play_until_the_end(game, [3, 1])

        self.assertEqual((state["result"], state["winner"]), ("win", "solo"))

    async def test_draw(self, _timer):
        game = await self.computer_game()

        state = await self.play_until_the_end(game, [1, 1])

        self.assertEqual((state["result"], state["winner_id"]), ("draw", None))

    async def test_score_limit_wins_before_the_time(self, _timer):
        game = await self.computer_game(duration_minutes=5, target_score=3)
        human = await self.connect(game, self.human)
        await self.start_playing(human)
        session = consumers.games[consumers.group_name(game.id)]
        session.score[:] = [2, 0]
        session.serve_at = None
        session.ball.x, session.ball.vx = 820, 300  # the computer missed

        await self.tick(0.02, steps=2)

        state = await self.latest(human)
        self.assertEqual((state["phase"], state["winner"], state["finish_reason"]), ("finished", "solo", "score"))
        self.assertGreater(state["time_left"], 290)
        await game.arefresh_from_db()
        self.assertEqual((game.leftPlayerScore, game.winner_id), (3, self.human.id))
        await human.disconnect()

    async def test_game_left_during_play_still_ends_and_is_freed(self, _timer):
        game = await self.two_player_game()
        left = await self.connect(game, self.human)
        right = await self.connect(game, self.friend)
        await self.start_playing(left, right)
        await left.disconnect()
        await right.disconnect()
        self.assertIn(consumers.group_name(game.id), consumers.games)

        await self.tick(61)
        await self.tick()

        self.assertNotIn(consumers.group_name(game.id), consumers.games)
        await game.arefresh_from_db()
        self.assertTrue(game.is_finish)

    async def test_empty_waiting_room_is_freed(self, _timer):
        game = await self.two_player_game()
        left = await self.connect(game, self.human)
        await self.tick()
        self.assertIn(consumers.group_name(game.id), consumers.games)

        await left.disconnect()
        await self.tick()

        self.assertNotIn(consumers.group_name(game.id), consumers.games)
        await game.arefresh_from_db()
        self.assertFalse(game.is_finish)  # the challenge is still open

    async def test_42_users_are_identified_by_their_jwt(self, _timer):
        self.human.id_42 = 4242
        await self.human.asave()
        game = await self.computer_game()
        token = generate_jwt_token({"id": 4242})
        human = await self.connect(game, headers=[(b"cookie", f"jwt_token={token}".encode())])

        await self.send(human, type="ready")

        self.assertEqual((await self.latest(human))["phase"], "countdown")
        await human.disconnect()
        await self.stop_game_loops()

    async def test_anonymous_visitor_cannot_press_ready(self, _timer):
        game = await self.two_player_game()
        visitor = await self.connect(game)

        await self.send(visitor, type="ready")

        self.assertEqual((await self.latest(visitor))["ready"], [])
        await visitor.disconnect()
        await self.stop_game_loops()
