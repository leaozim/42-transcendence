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
# broadcast = None

class BroadcastConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()

    async def connect(self):
        await self.accept()
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_broadcast"


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
        await ball.move()
        left_player_velocity = text_data_json.get("left_player_velocity", {})
        right_player_velocity = text_data_json.get("right_player_velocity", {})
        await right_paddle.set_paddle_velocity(right_player_velocity.get('x', 0), right_player_velocity.get('y', 0))
        await right_paddle.move()
        await left_paddle.set_paddle_velocity(left_player_velocity.get('x', 0), left_player_velocity.get('y', 0))
        print(left_paddle.velocity)
        await left_paddle.move()

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "game_update",
            "data": {
                "ball_x": ball.position.x,
                "ball_y": ball.position.y,
                "left_player_position_x": left_paddle.position.x,
                "left_player_position_y": left_paddle.position.y,
                "right_player_position_x": right_paddle.position.x,
                "right_player_position_y": right_paddle.position.y
            }
        })

    # async def game_loop(self):
    #     while True:
    #         await ball.move()
    #         await self.channel_layer.group_send(self.room_group_name, {
    #             "type": "game_update",
    #             "data": {
    #                 "ball_x": ball.position.x,
    #                 "ball_y": ball.position.y
    #             }
    #         })


    # async def update_ball_loop(self):
        # while True:
        #     ball.move()
        #     await self.send(
        #         text_data=json.dumps(
        #         {
        #             'type': 'game_update',
        #             'data': {
        #                 'ball_x': ball.position.x,
        #                 'ball_y': ball.position.y,
        #             }
        #         })
        #     )

# class Player1Consumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
#         self.room_group_name = f"game_{self.room_id}_player1"
#         self.broadcast_group_name = f"game_{self.room_id}_broadcast"

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)

#         # Processar dados, se necessário

#         # Envie para o grupo de transmissão geral
#         await self.channel_layer.group_send(
#             self.broadcast_group_name, {
#                 'type': 'player1_update',
#                 'data': text_data_json,
#             }
#         )

#     async def player1_update(self, event):
#         await self.send(text_data=json.dumps(event['data']))

# class Player2Consumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
#         self.room_group_name = f"game_{self.room_id}_player2"
#         self.broadcast_group_name = f"game_{self.room_id}_broadcast"

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)

#         # Processar dados, se necessário

#         # Envie para o grupo de transmissão geral
#         await self.channel_layer.group_send(
#             self.broadcast_group_name, {
#                 'type': 'game_update',
#                 'data': text_data_json,
#             }
#         )

#     async def player2_update(self, event):
#         await self.send(text_data=json.dumps(event['data']))