import json
from srcs_user.models import User
from srcs_chat.models import Chat

from srcs_message.services import add_message
from asgiref.sync import sync_to_async
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed
from channels.generic.websocket import AsyncWebsocketConsumer
from srcs_user.services import find_one_intra
from channels.db import database_sync_to_async

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
        
        await self.channel_layer.group_send(
		    self.room_group_name, {
            'type': 'chat_message', 
            'message': message,
            'user_id': user.id, 
            'username': user.username,
            'avatar': user.avatar,
         }
		)
        await self.save_message_to_db(chat_id, message, user_id)


    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        user_id = event["user_id"]
        user_avatar = event["avatar"]
        await self.send(text_data=json.dumps({"message": message, "username": username, "user_id": user_id, "user_avatar": user_avatar}))

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
    
    @database_sync_to_async
    def save_message_to_db(self, chat_id, message, user_id):
        db_insert =  add_message(chat_id, message, user_id)
        return db_insert
    



USERNAME = 0
AVATAR = 1
MESSAGE = 2

# message = {
#     'chat': {
#             2: { #id do chat
#                 2: [ #id do user que esta recebendo a mensagem
#                     'username',
#                     'avatar', 
#                     'message'
#                     ],
#                 3: []
#             }
#         },
#     'check_chat': True, #quando tiver index no chat ele fica true
#     'notifications': {  
#             1: [ #id do user que ta recebendo notificaçao 
#                 {
#                     2 : [ # dados do user que ta enviando a mensagem 
#                         'username',
#                         'avatar',  
#                         ]
#                 },
#                 {
#                     4 : [
#                         'username',
#                         'avatar',  
#                         ]
#                 }                      
#             ],
#         },
#     'check_notications': True,
#     'tournament': {},
#     'check_tournament': False
# }   
messages = {
    'chat': {},
    'check_chat': False,
    'notifications': {},
    'check_notifications': False,
    'tournament': {},
    'check_tournament': False
}   
class ChatConsumerUpdate(AsyncWebsocketConsumer):
    async def connect(self):

        self.group_name = "chat_update"
        
        await self.channel_layer.group_add(
		    self.group_name, self.channel_name
		)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
		    self.group_name, self.channel_name
		)

    async def receive(self, text_data):
        print(" ssssssssssssssssssssssssssssssssssssssss")

        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        chat_id = text_data_json["chat_id"]
        user_id = text_data_json["user_id"]
        other_user_id = text_data_json["other_user_id"]
        other_user_avatar = text_data_json["other_user_avatar"]
        other_user_username = text_data_json["other_user_username"]

        print(chat_id)
        print(message)

        # user_id = self.scope['user'].id
        # if user_id is None:
        #     user_id = await self.get_user_id_from_cookie()
        user = await sync_to_async(User.objects.get)(id=user_id)
        chat = await sync_to_async(Chat.objects.get)(id=chat_id)
        print(" ssssssssssssssssssssssssssssssssssssssss")
        # print(other_user)
        messages['chat'][chat_id] = {
            other_user_id: [
                other_user_username,
                other_user_avatar,
                message
            ]
        }
        messages['check_chat'] = True 
        
        if other_user_id in messages['notifications']:
            if user.id not in messages['notifications'][other_user_id]:     
                # messages['notifications'][other_user_id][user.id].append([user.username, user.avatar])
                messages['notifications'][other_user_id] = {
                    user.id : [
                        user.username,
                        user.avatar
                    ]
                }
        else:
            messages['notifications'][other_user_id] = {
                user.id : [
                    user.username,
                    user.avatar
                ]
            }
            
        messages['check_notifications'] = True 

        print(json.dumps(messages, indent=4))
        # await self.channel_layer.group_send(
		#     self.room_group_name, {
        #     'chat': {
        #             chat_id: { #id do chat
        #                 2: [ #id do user que esta recebendo a mensagem
        #                     'username',
        #                     'avatar', 
        #                     'message'
        #                     ],
        #                 3: []
        #             }
        #         },
        #     'check_chat': True, #quando tiver index no chat ele fica true
        #     'notifications': {  
        #             1: [ #id do user que ta recebendo notificaçao 
        #                 {
        #                     2 : [ # dados do user que ta enviando a mensagem 
        #                         'username',
        #                         'avatar',  
        #                         ]
        #                 },
        #                 {
        #                     4 : [
        #                         'username',
        #                         'avatar',  
        #                         ]
        #                 }                      
        #             ],
        #         },
        #     'check_notications': True,
        #     'tournament': {},
        #     'check_tournament': False
        #     }   
         
		# )
        # await self.save_message_to_db(room_id, message, user_id)

    async def chat_message_update(self, event):
        user_id = event.get("user_id")
        data_receiving_user = event.get("data_receiving_user")
        data_sender_user = event.get("data_sender_user")
        await self.send(text_data=json.dumps({"user_id": user_id, "data_receiving_user": data_receiving_user, "data_sender_user": data_sender_user}, ))
