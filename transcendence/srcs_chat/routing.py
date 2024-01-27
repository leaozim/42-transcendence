from django.urls import re_path

from . import consumers
from srcs_game import consumers as consugame

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]