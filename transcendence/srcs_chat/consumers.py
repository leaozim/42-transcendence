import json
from srcs_user.models import User
from srcs_message.services import add_message
from asgiref.sync import sync_to_async
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed
from channels.generic.websocket import AsyncWebsocketConsumer
from srcs_user.services import find_one_intra
from srcs_chat.services import get_updated_user_list

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        await self.channel_layer.group_add(
		    self.room_group_name, self.channel_name
		)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
		    self.room_group_name, self.channel_name
		)
        
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = self.scope['user'].id

        if user_id is None:
            user_id = await self.get_user_id_from_cookie()

        chat_id = int(self.room_id)
        user = await sync_to_async(User.objects.get)(id=user_id)
        user_list = await sync_to_async(get_updated_user_list)(user.id, user.username)
        print(user_list)
        await self.save_message_to_db(chat_id, message, user_id)
        await self.channel_layer.group_send(
		    self.room_group_name, {
            'type': 'chat_message', 
            'message': message,
            'user_id': user.id, 
            'username': user.username,
            'avatar': user.avatar,
            'users': user_list

         }
		)
        
    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        user_id = event["user_id"]
        user_avatar = event["avatar"]
        users = event["users"]
        await self.send(text_data=json.dumps({"message": message, "username": username, "user_id": user_id, "user_avatar": user_avatar,  "users": users}))

    async def get_user_id_from_cookie(self):
        cookie_header = next((value for name, value in self.scope['headers'] if name == b'cookie'), None)
        
        if cookie_header:
            cookie_str = cookie_header.decode('utf-8')
            parts = cookie_str.split("jwt_token=")
            
            if len(parts) > 1:
                jwt_token = parts[1].split(";")[0]
                
                if jwt_token:
                    payload = await sync_to_async(verify_jwt_token)(jwt_token)
                    user = await sync_to_async(find_one_intra)(payload["id_42"])
                    return user.id
        return None
    
    async def save_message_to_db(self, chat_id, message, user_id):
        db_insert = await sync_to_async(add_message)(chat_id, message, user_id)
        return db_insert
    
