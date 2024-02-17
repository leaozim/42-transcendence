from django.urls import re_path

from srcs_chat.consumers import ChatConsumer
from srcs_game.consumers import BroadcastConsumer#, Player1Consumer, Player2Consumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\d+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/game/broadcast/(?P<room_id>\d+)/$", BroadcastConsumer.as_asgi()),
    # re_path(r"ws/game/player1/(?P<room_id>\d+)/$", Player1Consumer.as_asgi()),
    # re_path(r"ws/game/player2/(?P<room_id>\d+)/$", Player2Consumer.as_asgi()),
]