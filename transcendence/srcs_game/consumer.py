import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MultiplayerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}"

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
        left_player = ball_data.get('left_player_id', 0)
        right_player = ball_data.get('right_player_id', 0)

        print(f'X: {x}\tY: {y}\tleftPlayer: {left_player}\trightPlayer: {right_player}')

        await self.channel_layer.group_send(
		    self.room_group_name, {
                'type': 'game_update', 
                'data': text_data_json,
            }
		)

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))