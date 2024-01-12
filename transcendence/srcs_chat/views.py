from django.shortcuts import render
from srcs_chat.models import Chat
from django.http import HttpResponseForbidden
# from srcs_auth.decorators import login_or_jwt_required
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return render(request, "chat/index.html")

@login_required(login_url="/")
def room(request, room_name):
    chat = Chat.objects.get(id=int(room_name))
    messages = chat.message_set.all().order_by('timestamp')
    sorted_messages = sorted(messages, key=lambda x: x.timestamp)
    return render(request, "chat/room.html", context={"messages": sorted_messages, "room_name": room_name})
