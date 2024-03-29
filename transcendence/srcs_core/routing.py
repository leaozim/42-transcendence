from django.urls import path, re_path
from srcs_chat.consumers import ChatConsumer, ChatConsumerUpdate
from srcs_game.consumers import BroadcastConsumer

websocket_urlpatterns = [
    path("ws/chat/<int:room_id>/<int:user_id>", ChatConsumer.as_asgi()),
    re_path(r"ws/game/broadcast/(?P<room_id>\d+)/$", BroadcastConsumer.as_asgi()),
    path("ws/chat_update/<int:user_id>", ChatConsumerUpdate.as_asgi()),
]
