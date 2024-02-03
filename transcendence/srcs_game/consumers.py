import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BroadcastConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_broadcast"

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

        player_data = text_data_json.get('player', {})
        is_left_player = player_data.get('left', 0) == 1

        if is_left_player:
            print("Recebido do jogador esquerdo:")
            print(f"Paddle X: {player_data.get('paddle', {}).get('x')}")
            print(f"Paddle Y: {player_data.get('paddle', {}).get('y')}")
        else:
            print("Recebido do jogador direito:")
            print(f"Paddle X: {player_data.get('paddle', {}).get('x')}")
            print(f"Paddle Y: {player_data.get('paddle', {}).get('y')}")

        await self.channel_layer.group_send(
		    self.room_group_name, {
                'type': 'game_update', 
                'data': text_data_json,
            }
		)

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

class Player1Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_player1"

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

        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'game_update',
                'data': text_data_json,
            }
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

class Player2Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_player2"

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

        await self.channel_layer.group_send(
            self.room_group_name, {
                'type': 'game_update',
                'data': text_data_json,
            }
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))