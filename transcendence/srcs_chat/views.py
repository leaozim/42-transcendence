from django.shortcuts import render, redirect, get_object_or_404
from srcs_chat.models import Chat
from django.http import HttpResponseForbidden
from srcs_auth.decorators import two_factor_required
from django.contrib.auth.decorators import login_required
from srcs_chat import services
from srcs_user.models import User
from django.http import JsonResponse
from django.http import Http404


@login_required
@two_factor_required
def index(request):
    return render(request, "chat/index.html")

@login_required
@two_factor_required
def room(request, room_name):
    chat = Chat.objects.get(id=int(room_name))
    if not services.is_user_in_chat(chat, request.user):
        raise Http404
    messages = chat.message_set.all().order_by('timestamp')
    sorted_messages = sorted(messages, key=lambda x: x.timestamp)
    return render(request, "chat/room.html", context={"messages": sorted_messages, "room_name": room_name})


def listar_chats(request):
    user_id = request.user.id
    chats = services.find_open_chats(user_id)
    return render(request, 'listar_chats.html', {'chats': chats})


def list_users(request):
    users = User.objects.all()
    return render(request, 'chat/list_users.html', {'users': users})


def create_or_open_chat(request, user_id):
    user_id_logged_in = request.user.id 

    chat = Chat.objects.filter(users_on_chat=user_id_logged_in).filter(users_on_chat=user_id).first()
    if not chat:
        services.open_chat(user_id_logged_in, user_id)
        
    return JsonResponse({'room_name': chat.id})
