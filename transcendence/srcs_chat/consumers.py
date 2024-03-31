import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from srcs_auth.jwt_token import verify_jwt_token
from srcs_chat.models import Chat
from srcs_chat.services import get_validated_chat_and_user
from srcs_message.models import Message
from srcs_user.models import User, BlockedUser
from srcs_user.services import find_one_intra


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_prefix = f"chat_{self.room_id}"
        self.room_group_name = f"{self.room_prefix}_{self.user_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def _get_receiver_id(self, chat_id, user_id) -> int:
        chat = await sync_to_async(Chat.objects.get)(id=chat_id)
        query = await sync_to_async(chat.users_on_chat.filter)(~Q(id=user_id))

        return await sync_to_async(query.first)()
    
    async def check_blocked_user(self, user_id, receiver_id):
        blocked_user = await sync_to_async(BlockedUser.objects.filter)(
            blocked_by_id=user_id,
            blocked_user_id=receiver_id
        )

        blocked_by_user = await sync_to_async(BlockedUser.objects.filter)(
            blocked_by_id=receiver_id,
            blocked_user_id=user_id
        )

        return blocked_user, blocked_by_user

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = self.scope["user"].id

        if user_id is None:
            user_id = await self.get_user_id_from_cookie()

        chat_id = int(self.room_id)
        user = await sync_to_async(User.objects.get)(id=user_id)
        receiver = await self._get_receiver_id(chat_id, user_id)

        blocked_user, blocked_by_user = await self.check_blocked_user(user.id, receiver.id)
        b_user = await sync_to_async(blocked_user.first)()
        b_b_user = await sync_to_async(blocked_by_user.first)()
        if b_user or b_b_user:
            return
        
        await self.channel_layer.group_send(
            f"{self.room_prefix}_{receiver.id}",
            {
                "type": "chat_message",
                "message": message,
                "user_id": user.id,
                "username": user.username,
                "avatar": user.avatar,
            },
        )
        await self.save_message_to_db(chat_id, message, user_id)

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "username": event["username"],
                    "user_id": event["user_id"],
                    "avatar": event["avatar"],
                }
            )
        )

    async def get_user_id_from_cookie(self):
        cookie_header = next(
            (value for name, value in self.scope["headers"] if name == b"cookie"), None
        )

        if cookie_header:
            cookie_str = cookie_header.decode("utf-8")
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
        chat, user = get_validated_chat_and_user(chat_id, user_id)
        return Message.objects.create(chat_id=chat.id, content=message, user_id=user.id)


class ChatConsumerUpdate(AsyncWebsocketConsumer):
    async def connect(self):

        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.group_name = f"chat_update.{user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_message_update(self, event):
        await self.send(
            bytes_data=json.dumps({"data": event.get("data")}).encode("utf-8")
        )
