from django.urls import re_path

from srcs_chat.consumers import ChatConsumer
from srcs_game.consumer import MultiplayerConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/game/(?P<room_name>[^/]+)/$", MultiplayerConsumer.as_asgi()),
]