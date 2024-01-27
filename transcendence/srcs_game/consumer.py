import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MultiplayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"game_1"

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

        ball_data = text_data_json.get('ball', {})
        
        # Adicionar lógica para processar inputs
        # Trazer lógica de loop do jogo para cá

        x = ball_data.get('x', 0)
        y = ball_data.get('y', 0)

        print(f'X: {x}\tY: {y}')

        await self.channel_layer.group_send(
		    self.room_group_name, {
                'type': 'game_update', 
                'data': text_data_json,
            }
		)

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))