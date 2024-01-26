from django.shortcuts import render, redirect, get_object_or_404
from srcs_chat.models import Chat
from django.http import HttpResponseForbidden
from srcs_auth.decorators import two_factor_required
from django.contrib.auth.decorators import login_required
from srcs_chat import services
from srcs_user.models import User
from srcs_message.models import Message

from django.http import JsonResponse
from django.http import Http404


@login_required
@two_factor_required
def room(request, room_name):
    chat = Chat.objects.get(id=int(room_name))
    if not services.is_user_in_chat(chat, request.user):
        raise Http404
    messages = chat.message_set.all().order_by('timestamp')
    sorted_messages = sorted(messages, key=lambda x: x.timestamp)
    return render(request, "chat/room.html", context={"messages": sorted_messages, "room_name": room_name})


def chats_list(request):
    user_chats = Chat.objects.filter(users_on_chat=request.user)

    user_chats = request.user.users_chats.all()
    users_in_chats = User.objects.filter(users_chats__in=user_chats).distinct()

    return render(request, 'chat/chats_list.html', {'users_in_chats': users_in_chats})


def create_or_open_chat(request, user_id):
    user_id_logged_in = request.user.id 
    
    chat = Chat.objects.filter(users_on_chat=user_id_logged_in).filter(users_on_chat=user_id).first()
    if not chat: 
        chat = services.open_chat(user_id_logged_in, user_id)
        
    return JsonResponse({'room_name': chat.id})
