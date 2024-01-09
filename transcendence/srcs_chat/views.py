from django.shortcuts import render
from srcs_chat.models import Chat
# from srcs_message.models import Message
from srcs_auth.middleware import JWTAuthenticationMiddleware
from srcs_chat.services import is_user_in_chat
from django.http import HttpResponseForbidden

def index(request):
    return render(request, "chat/index.html")


def room(request, room_name):
    chat = Chat.objects.get(id=int(room_name))
    messages = chat.message_set.all().order_by('timestamp')
    sorted_messages = sorted(messages, key=lambda x: x.timestamp)
    return render(request, "chat/room.html", context={"messages": sorted_messages, "room_name": room_name})
