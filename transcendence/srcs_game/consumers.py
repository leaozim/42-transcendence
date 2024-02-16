import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from static.game.scripts.Ball import Ball

ball = Ball()
broadcast = None

class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_broadcast"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.update_ball_loop()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    async def receive(self, event):
        await self.update_ball_loop()

    async def update_ball_loop(self):
        ball.move()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'data': {
                    'ball_x': ball.position.x,
                    'ball_y': ball.position.y,
                }
            }
        )

class Player1Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_player1"
        self.broadcast_group_name = f"game_{self.room_id}_broadcast"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Processar dados, se necessário

        # Envie para o grupo de transmissão geral
        await self.channel_layer.group_send(
            self.broadcast_group_name, {
                'type': 'player1_update',
                'data': text_data_json,
            }
        )

    async def player1_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

class Player2Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_player2"
        self.broadcast_group_name = f"game_{self.room_id}_broadcast"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        # Processar dados, se necessário

        # Envie para o grupo de transmissão geral
        await self.channel_layer.group_send(
            self.broadcast_group_name, {
                'type': 'game_update',
                'data': text_data_json,
            }
        )

    async def player2_update(self, event):
        await self.send(text_data=json.dumps(event['data']))