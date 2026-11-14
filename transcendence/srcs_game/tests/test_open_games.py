from datetime import timedelta
from unittest import mock

from asgiref.sync import sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from srcs_core.routing import websocket_urlpatterns
from srcs_game import consumers
from srcs_game.models import Game
from srcs_game.services import create_computer_game, create_game
from srcs_game.session import GameSession
from srcs_user.models import User

MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


def create_bot():
    return User.objects.create_user("pong (BOT)", "", None, id=1)


@mock.patch.object(Game, "start_connection_timer")
class OpenGamesPanelTestCase(TestCase):
    def setUp(self):
        consumers.games.clear()
        create_bot()
        self.alice = User.objects.create_user("alice", "a@example.com", "Al1ce-password!")
        self.bob = User.objects.create_user("bob", "b@example.com", "B0b-password!")

    def home_for(self, user):
        self.client.force_login(user, backend=MODEL_BACKEND)
        return self.client.get("/")

    def test_challenged_player_sees_the_game_on_the_home_page(self, _timer):
        game = create_game(self.alice, self.bob, duration_minutes=2, target_score=5)

        response = self.home_for(self.bob)

        self.assertContains(response, 'id="open-games"')
        self.assertContains(response, "alice challenged you!")
        self.assertContains(response, "2 minutes · first to 5 points")
        self.assertContains(response, f'href="{reverse("srcs_game:room", args=[game.id])}"')
        self.assertContains(response, "Join")
        self.assertContains(response, f'data-cancel-game="{reverse("srcs_game:cancel", args=[game.id])}"')
        self.assertContains(response, "Decline")

    def test_challenger_sees_the_game_too(self, _timer):
        create_game(self.alice, self.bob)

        response = self.home_for(self.alice)

        self.assertContains(response, "You challenged bob")
        self.assertContains(response, "bob is not in the game room.")
        self.assertRegex(response.content.decode(), r"data-cancel-game=\"[^\"]+\">\s*Cancel\s*<")

    def test_presence_of_the_opponent_in_the_game_room(self, _timer):
        game = create_game(self.alice, self.bob)
        session = GameSession(self.alice.id, self.bob.id, 60)
        session.connect(self.alice.id)
        consumers.games[consumers.group_name(game.id)] = session

        self.assertContains(self.home_for(self.bob), "alice is in the game room.")

    def test_games_not_listed(self, _timer):
        create_computer_game(self.alice)
        finished = create_game(self.alice, self.bob)
        finished.is_finish = True
        finished.save()
        abandoned = create_game(self.alice, self.bob)
        abandoned.started_at = timezone.now() - timedelta(minutes=10)
        abandoned.save()

        response = self.home_for(self.alice)

        self.assertNotContains(response, 'class="open-games-panel"')

    def test_game_in_progress(self, _timer):
        game = create_game(self.alice, self.bob)
        game.started_at = timezone.now()
        game.save()

        response = self.home_for(self.bob)

        self.assertContains(response, "Playing against alice")
        self.assertContains(response, "Rejoin")
        self.assertNotContains(response, "data-cancel-game")

    def test_panel_fragment(self, _timer):
        create_game(self.alice, self.bob)
        self.client.force_login(self.bob, backend=MODEL_BACKEND)

        response = self.client.get(reverse("srcs_game:open_games"))

        self.assertContains(response, "alice challenged you!")
        self.assertNotContains(response, "<html")
        self.client.logout()
        self.assertEqual(self.client.get(reverse("srcs_game:open_games")).status_code, 302)

    def test_panel_in_brazilian_portuguese(self, _timer):
        create_game(self.alice, self.bob, duration_minutes=3, target_score=1)
        self.client.cookies["django_language"] = "pt-br"

        response = self.home_for(self.bob)

        self.assertContains(response, "alice desafiou você!")
        self.assertContains(response, "3 minutos · vence quem fizer 1 ponto")
        self.assertContains(response, "Recusar")


@mock.patch.object(Game, "start_connection_timer")
class CancelGameTestCase(TestCase):
    def setUp(self):
        create_bot()
        self.alice = User.objects.create_user("alice", "a@example.com", "Al1ce-password!")
        self.bob = User.objects.create_user("bob", "b@example.com", "B0b-password!")
        self.carol = User.objects.create_user("carol", "c@example.com", "C4rol-password!")
        self.game = create_game(self.alice, self.bob)
        self.url = reverse("srcs_game:cancel", args=[self.game.id])

    def post_as(self, user):
        self.client.force_login(user, backend=MODEL_BACKEND)
        return self.client.post(self.url)

    def test_creator_cancels(self, _timer):
        self.assertEqual(self.post_as(self.alice).json(), {"canceled": True})
        self.game.refresh_from_db()
        self.assertTrue(self.game.is_finish)
        self.assertIsNone(self.game.winner)

    def test_opponent_declines(self, _timer):
        self.assertEqual(self.post_as(self.bob).status_code, 200)

    def test_others_cannot_cancel(self, _timer):
        self.assertEqual(self.post_as(self.carol).status_code, 403)
        self.game.refresh_from_db()
        self.assertFalse(self.game.is_finish)

    def test_started_and_tournament_games_cannot_be_canceled(self, _timer):
        self.game.started_at = timezone.now()
        self.game.save()
        self.assertEqual(self.post_as(self.alice).status_code, 403)

        tournament_game = create_game(self.alice, self.bob)
        tournament_game.tournament_id = 1
        tournament_game.save()
        response = self.client.post(reverse("srcs_game:cancel", args=[tournament_game.id]))
        self.assertEqual(response.status_code, 403)

    def test_get_is_not_allowed(self, _timer):
        self.client.force_login(self.alice, backend=MODEL_BACKEND)
        self.assertEqual(self.client.get(self.url).status_code, 405)


@mock.patch.object(Game, "start_connection_timer")
class LiveUpdatesTestCase(TransactionTestCase):
    def setUp(self):
        consumers.games.clear()
        create_bot()
        self.alice = User.objects.create_user("alice", "a@example.com", "Al1ce-password!")
        self.bob = User.objects.create_user("bob", "b@example.com", "B0b-password!")
        self.application = URLRouter(websocket_urlpatterns)

    async def open(self, path, user=None):
        communicator = WebsocketCommunicator(self.application, path)
        if user is not None:
            communicator.scope["user"] = user
        connected, _ = await communicator.connect()
        return communicator, connected

    async def test_lobby_requires_login(self, _timer):
        communicator, connected = await self.open("/ws/lobby/")
        self.assertFalse(connected)

    async def test_new_challenge_pings_the_opponent(self, _timer):
        lobby, connected = await self.open("/ws/lobby/", self.bob)
        self.assertTrue(connected)

        await sync_to_async(create_game)(self.alice, self.bob)

        self.assertEqual(await lobby.receive_json_from(timeout=2), {"type": "games_changed"})
        await lobby.disconnect()

    async def test_opponent_entering_the_room_pings_the_lobby(self, _timer):
        game = await sync_to_async(create_game)(self.alice, self.bob)
        lobby, _ = await self.open("/ws/lobby/", self.bob)

        room, _ = await self.open(f"/ws/game/broadcast/{game.id}/", self.alice)

        self.assertEqual(await lobby.receive_json_from(timeout=2), {"type": "games_changed"})
        await room.disconnect()
        await lobby.disconnect()

    async def test_decline_tells_the_player_waiting_in_the_room(self, _timer):
        game = await sync_to_async(create_game)(self.alice, self.bob)
        room, _ = await self.open(f"/ws/game/broadcast/{game.id}/", self.alice)
        await room.receive_json_from()  # initial state

        await sync_to_async(self.client.force_login)(self.bob, backend=MODEL_BACKEND)
        response = await sync_to_async(self.client.post)(reverse("srcs_game:cancel", args=[game.id]))

        self.assertEqual(response.status_code, 200)
        message = await room.receive_json_from(timeout=2)
        while message.get("phase") != "canceled":
            message = await room.receive_json_from(timeout=2)
        self.assertEqual(message, {"phase": "canceled", "result": "annulled"})
        self.assertNotIn(consumers.group_name(game.id), consumers.games)
        await room.disconnect()
