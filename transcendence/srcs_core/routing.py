from django.urls import re_path

from srcs_chat.consumers import ChatConsumer
from srcs_game.consumers import BroadcastConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>\d+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/game/broadcast/(?P<room_id>\d+)/$", BroadcastConsumer.as_asgi()),
]