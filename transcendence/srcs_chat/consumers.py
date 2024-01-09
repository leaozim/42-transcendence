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
		    self.room_group_name, {
            'type': 'chat_message', 
            'message': message,
            'user_id': user.id, 
            'username': user.username,
         }
		)

    def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        user_id = event["user_id"]
        self.send(text_data=json.dumps({"message": message, "username": username, "user_id": user_id}))

    def get_user_id_from_cookie(self):
        cookie_header = next((value for name, value in self.scope['headers'] if name == b'cookie'), None)
        if cookie_header:
            cookie_str = cookie_header.decode('utf-8')
            parts = cookie_str.split("jwt_token=")
            if len(parts) > 1:
                jwt_token = parts[1].split(";")[0]
                if jwt_token:
                    user = verify_jwt_token(jwt_token)
                    return user.id
        return None
    
    def save_message_to_db(self, chat_id, message, user_id):
        db_insert = add_message(chat_id, message, user_id)
        return db_insert