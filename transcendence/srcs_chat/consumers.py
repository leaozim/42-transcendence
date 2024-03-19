import json
from srcs_user.models import User
from srcs_chat.models import Chat

from srcs_message.services import add_message
from asgiref.sync import sync_to_async
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed
from channels.generic.websocket import AsyncWebsocketConsumer
from srcs_user.services import find_one_intra
from channels.db import database_sync_to_async
from urllib.parse import urlparse

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
#     'tournament': {
#               1 : { # tournament Id, utilizado para verificar se o jogador está dentro do torneio e identificar o torneio da msg
#                      1 : [ # chat Id
#                          'username',
#                          'message'
#                      ]
#                  },
#               }
#     'check_tournament': False
# }   
messages = {
    'type': '',
    'chat': {},
    'check_chat': False,
    'notifications': {},
    'check_notifications': False,
    'tournament': {
        'global': {},
        'individual': {}
        },
    'check_tournament': False
}   
class ChatConsumerUpdate(AsyncWebsocketConsumer):
    async def connect(self):

        self.group_name = "update"
        
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
        print(urlparse(self.scope['path']).path) # será usado para checar se o user está no chat ou não

        text_data_json = json.loads(text_data)
        # print(text_data_json)
        # broadcast_type = text_data_json["type"]
        broadcast_type = "chat"
        if broadcast_type == "chat":
            message = text_data_json["message"]
            chat_id = str(text_data_json["chat_id"])
            user_id = str(text_data_json["user_id"])
            other_user_id = str(text_data_json["other_user_id"])
            other_user_avatar = text_data_json["other_user_avatar"]
            other_user_username = text_data_json["other_user_username"]


            user = await sync_to_async(User.objects.get)(id=int(user_id))
            
            if chat_id in messages['chat']:
                if other_user_id in messages['chat'][chat_id]:
                    messages['chat'][chat_id][other_user_id].append([other_user_username, other_user_avatar, message])
                else:
                    messages['chat'][chat_id][other_user_id] = [[other_user_username, other_user_avatar, message]]
            else:
                messages['chat'][chat_id] = {other_user_id: [[other_user_username, other_user_avatar, message]]}

            messages['check_chat'] = True 
            
            if other_user_id in messages['notifications']:
                if str(user.id) not in messages['notifications'][other_user_id]:     
                    messages['notifications'][other_user_id] = {
                        str(user.id) : [
                            user.username,
                            user.avatar
                        ]
                    }
            else:
                messages['notifications'][other_user_id] = {
                    str(user.id) : [
                        user.username,
                        user.avatar
                    ]
                }
            messages['check_notifications'] = True
            # message_json = json.dumps(messages)
            # print(messages)
            await self.channel_layer.group_send(
            self.group_name ,{
                    "type": "chat_message_update",  # Tipo de mensagem a ser enviada
                    "messages": messages  # Dados a serem enviados
                }
            )
            await self.save_message_to_db(int(chat_id), message, int(user_id))

        if broadcast_type == 'tournament':
            pass
       

            

        # print(json.dumps(messages, indent=4))

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

    async def chat_message_update(self, event):
        messages = event["messages"]
        await self.send(text_data=json.dumps(messages))
    
    @database_sync_to_async
    def save_message_to_db(self, chat_id, message, user_id):
        db_insert =  add_message(chat_id, message, user_id)
        return db_insert

