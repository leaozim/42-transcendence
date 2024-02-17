import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from static.game.scripts.Ball import Ball
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

ball = Ball()
# broadcast = None

class BroadcastConsumer(AsyncWebsocketConsumer):
    update_lock = asyncio.Lock()

    async def connect(self):
        await self.accept()
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_broadcast"


        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.send(text_data=json.dumps({"type": "playerId", "playerId": 'cavalinho'}))

        asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type", "")
        print('receive: ')
        print(message_type)

    async def game_loop(self):
        while True:
            ball.move()
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "game_update",
                "data": {
                    "ball_x": ball.position.x,
                    "ball_y": ball.position.y
                }
            })


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