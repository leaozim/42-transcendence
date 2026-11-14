import asyncio
import json
import logging
import time

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
'''
    Note que essa bola e raquete são diferentes pro python e pro js.
    O Js não possui lógica de jogo, apenas exibe o estado recebido e captura o input,
    enquanto o python contém a lógica do jogo (srcs_game/session.py e physics.py).
'''
from srcs_auth.channels_auth import resolve_user_id
from srcs_game.computer import ComputerPlayer
from srcs_game.models import Game
from srcs_game.notifications import lobby_group, notify_lobby
from srcs_game.physics import PLAYER_LEFT
from srcs_game.services import finish_game, mark_game_started
from srcs_game.session import FINISHED, PLAYING, WAITING, GameSession

logger = logging.getLogger(__name__)

'''
    Games being played in this process: group name -> GameSession.
    Kept in memory, so the server must run as a single process.
'''
games = {}

# The game loop runs at this rate and, during play, sends the state this often.
TICK_SECONDS = 1 / 60
# Longest simulated step: if the server stalls, the game slows down a little
# instead of the ball jumping.
MAX_STEP_SECONDS = 0.05
# Outside play the state is sent when it changes, and at least this often
# (for the countdown).
IDLE_BROADCAST_SECONDS = 0.25


def group_name(game_id):
    return f"game_{game_id}_broadcast"


async def broadcast(session, game_id, now):
    data = session.state(now)
    if "winner_id" in data:
        data["winner"] = session.names.get(data["winner_id"])
    await get_channel_layer().group_send(group_name(game_id), {"type": "game_update", "data": data})


async def run_game(game_id, session):
    """
    Game loop of one game: advances it in real time, saves when it starts and
    ends, and sends its state to the game room. It stops (and the game is
    forgotten) when the game is over or canceled, or when everybody left
    before it began. A game whose players leave during play still ends on
    time, and its result is saved.
    """
    key = group_name(game_id)
    last = time.time()
    last_broadcast = float("-inf")
    try:
        while games.get(key) is session:
            await asyncio.sleep(TICK_SECONDS)
            if games.get(key) is not session:
                break
            now = time.time()
            dt = min(max(now - last, 0.0), MAX_STEP_SECONDS)
            last = now

            if session.update(now, dt):
                await database_sync_to_async(mark_game_started)(game_id)
            if session.phase == FINISHED:
                games.pop(key, None)
                side = session.winner_side
                winner_id = None if side is None else session.players[side]
                await database_sync_to_async(finish_game)(game_id, session.score, winner_id)
                await broadcast(session, game_id, now)
                break
            if session.phase == PLAYING or session.changed or now - last_broadcast >= IDLE_BROADCAST_SECONDS:
                session.changed = False
                last_broadcast = now
                await broadcast(session, game_id, now)
            if session.sockets == 0 and session.phase == WAITING:
                games.pop(key, None)  # everybody left before the game began
                break
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Game loop of game %s stopped", game_id)
        games.pop(key, None)


def _direction(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0
    return (value > 0) - (value < 0)


class BroadcastConsumer(AsyncWebsocketConsumer):
    """
    One connection to a game room (players and spectators).

    Clients send {"type": "ready"} when the player presses Ready and
    {"type": "input", "direction": -1 | 0 | 1} when they press or release an
    arrow key. The game loop (run_game) sends them the state of the game.
    """

    async def connect(self):
        self.session = None
        self.room_id = int(self.scope["url_route"]["kwargs"]["room_id"])
        self.room_group_name = group_name(self.room_id)

        game = await database_sync_to_async(
            Game.objects.select_related("leftPlayer", "rightPlayer").filter(pk=self.room_id).first
        )()
        if game is None or game.is_finish:
            await self.close()  # refuses the connection
            return
        self.user_id = await resolve_user_id(self.scope)
        if not game.has_started:
            # Someone opened the room: the game is not a no-show (see Game.check_connection).
            game.has_started = True
            await database_sync_to_async(game.save)(update_fields=["has_started"])

        # No await between the lookup and the insertion: one session (and one
        # game loop) per game.
        self.session = games.get(self.room_group_name)
        if self.session is None:
            self.session = games[self.room_group_name] = self._new_session(game)
            self.session.task = asyncio.ensure_future(run_game(self.room_id, self.session))
        self.session.connect(self.user_id)

        # Accept only once the session is set up, so no message is lost.
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        if self.session.side(self.user_id) is not None:
            await notify_lobby(*self.session.players)

    @staticmethod
    def _new_session(game):
        computer = ComputerPlayer() if game.against_computer else None
        session = GameSession(
            game.leftPlayer_id,
            game.rightPlayer_id,
            game.duration_minutes * 60,
            game.target_score,
            computer,
        )
        session.names = {game.leftPlayer_id: game.leftPlayer.username, game.rightPlayer_id: game.rightPlayer.username}
        return session

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if self.session is None or games.get(self.room_group_name) is not self.session:
            return
        self.session.disconnect(self.user_id)
        if self.session.side(self.user_id) is not None:
            await notify_lobby(*self.session.players)

    async def receive(self, text_data):
        session = self.session
        if session is None or session.phase == FINISHED:
            return
        try:
            data = json.loads(text_data)
        except ValueError:
            return
        if not isinstance(data, dict):
            return

        kind = data.get("type")
        if kind == "ready":
            session.set_ready(self.user_id, time.time())
        elif kind == "input":
            session.set_direction(self.user_id, _direction(data.get("direction")))
        elif kind == "frame":
            # Page loaded before the game loop existed (cached script): it sends
            # its paddle velocity on every frame.
            key = "left_player_velocity" if session.side(self.user_id) == PLAYER_LEFT else "right_player_velocity"
            velocity = data.get(key) if isinstance(data.get(key), dict) else {}
            session.set_direction(self.user_id, _direction(velocity.get("y")))

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def game_canceled(self, event):
        # Sent by the cancel view: a player canceled or declined the game.
        games.pop(self.room_group_name, None)
        self.session = None
        await self.send(text_data=json.dumps({"phase": "canceled", "result": "annulled"}))


class LobbyConsumer(AsyncWebsocketConsumer):
    """Home page: tells the logged-in user when their open games change."""

    async def connect(self):
        self.group = None
        user_id = await resolve_user_id(self.scope)
        if user_id is None:
            await self.close()
            return
        self.group = lobby_group(user_id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.group:
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def lobby_changed(self, event):
        await self.send(text_data=json.dumps({"type": "games_changed"}))
