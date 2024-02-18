import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from static.game.scripts.Ball import Ball
from static.game.scripts.Paddle import Paddle
from static.game.scripts.Vector2 import Vector2
from static.game.scripts.constants import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

ball = Ball()
left_paddle = Paddle(LEFT_PADDLE_START_POSITION[0], LEFT_PADDLE_START_POSITION[1])
right_paddle = Paddle(RIGHT_PADDLE_START_POSITION[0], RIGHT_PADDLE_START_POSITION[1])
score = [0, 0]
# broadcast = None

games = {}

class BroadcastConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()

    async def connect(self):
        await self.accept()
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_broadcast"

        if self.room_group_name not in games:
            games[self.room_group_name] = {
                'ball': Ball(),
                'left_paddle': Paddle(LEFT_PADDLE_START_POSITION[0], LEFT_PADDLE_START_POSITION[1]),
                'right_paddle': Paddle(RIGHT_PADDLE_START_POSITION[0], RIGHT_PADDLE_START_POSITION[1]),
                'score': [0, 0]
                }
        self.ball = games[self.room_group_name]['ball']
        self.left_paddle = games[self.room_group_name]['left_paddle']
        self.right_paddle = games[self.room_group_name]['right_paddle']
        self.score = games[self.room_group_name]['score']


        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.send(text_data=json.dumps({"type": "playerId", "playerId": 'cavalinho'}))

        # asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        await self.ball.move()
        left_player_velocity = text_data_json.get("left_player_velocity", {})
        right_player_velocity = text_data_json.get("right_player_velocity", {})
        await self.right_paddle.set_paddle_velocity(right_player_velocity.get('x', 0), right_player_velocity.get('y', 0))
        await self.right_paddle.move()
        await self.left_paddle.set_paddle_velocity(left_player_velocity.get('x', 0), left_player_velocity.get('y', 0))
        await self.left_paddle.move()
        self.ball.checkPaddleCollision(self.left_paddle.position.x, self.left_paddle.position.y, PLAYER_LEFT)
        self.ball.checkPaddleCollision(self.right_paddle.position.x, self.right_paddle.position.y, PLAYER_RIGHT)
        if (self.ball.position.x > CANVAS_WIDTH):
            self.score[PLAYER_LEFT] += 1
            await self.ball.resetBall()

        if (self.ball.position.x < 0):
            self.score[PLAYER_RIGHT] += 1
            await self.ball.resetBall()

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "game_update",
            "data": {
                "ball_x": self.ball.position.x,
                "ball_y": self.ball.position.y,
                "left_player_position_x": self.left_paddle.position.x,
                "left_player_position_y": self.left_paddle.position.y,
                "right_player_position_x": self.right_paddle.position.x,
                "right_player_position_y": self.right_paddle.position.y,
                "score": self.score
            }
        })
