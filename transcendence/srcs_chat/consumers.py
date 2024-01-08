# import json

# from channels.generic.websocket import AsyncWebsocketConsumer

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     async def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({"message": message}))

import json

from channels.generic.websocket import WebsocketConsumer
from srcs_user.models import User
from srcs_message.services import add_message
from srcs_chat.models import Chat
from asgiref.sync import async_to_sync
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(
		    self.room_group_name, self.channel_name
		)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
		    self.room_group_name, self.channel_name
		)
        
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = self.scope['user'].id

        if user_id is None:
            user_id = self.get_user_id_from_cookie()

        chat_id = int(self.room_name)
        user = User.objects.get(id=user_id)
        self.save_message_to_db(chat_id, message, user_id)
        async_to_sync(self.channel_layer.group_send)(
		    self.room_group_name, {'type': 'chat_message', 'message': f'{user.username}: {message}'}
		)

    def chat_message(self, event):
        message = event["message"]

        self.send(text_data=json.dumps({"message": message}))

    def get_user_id_from_cookie(self):
        cookie_header = next((value for name, value in self.scope['headers'] if name == b'cookie'), None)
        print(cookie_header)
        if cookie_header:
            cookie_str = cookie_header.decode('utf-8')
            parts = cookie_str.split("jwt_token=")
            if len(parts) > 1:
                jwt_token = parts[1].split(";")[0]
            user = verify_jwt_token(jwt_token)
            return user.id
        return None
    
    def save_message_to_db(self, chat_id, message, user_id):
        db_insert = add_message(chat_id, message, user_id)
        db_insert.save()