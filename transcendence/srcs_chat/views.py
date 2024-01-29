from django.shortcuts import render, redirect, get_object_or_404
from srcs_chat.models import Chat
from django.http import HttpResponseForbidden
from srcs_auth.decorators import two_factor_required
from django.contrib.auth.decorators import login_required
from srcs_chat import services
from srcs_user.models import User
from srcs_message.models import Message
from django.db.models import Count

from django.http import JsonResponse
from django.http import Http404


@login_required
@two_factor_required
def open_chat(request, room_name):
    chat = Chat.objects.get(id=int(room_name))
    if not services.is_user_in_chat(chat, request.user):
        raise Http404
    messages = chat.message_set.all().order_by('timestamp')
    sorted_messages = sorted(messages, key=lambda x: x.timestamp)
    return render(request, "chat/open_chat.html", context={"messages": sorted_messages, "room_name": room_name})


def chats_list(request):
    user_chats = Chat.objects.filter(users_on_chat=request.user)

    users_in_chats = User.objects.filter(users_chats__in=user_chats).distinct()
    user_chats_with_message_count = user_chats.annotate(message_count=Count('message'))
    users_with_messages = []

    for chat in user_chats_with_message_count:
        if chat.message_count > 0:
            users_with_messages.extend(users_in_chats.filter(users_chats=chat))

    print(users_with_messages)
    return render(request, 'chat/list_of_chat_users.html', {'users_in_chats': users_with_messages})


def create_or_open_chat(request, user_id):
    user_id_logged_in = request.user.id 
    
    chat = Chat.objects.filter(users_on_chat=user_id_logged_in).filter(users_on_chat=user_id).first()
    if not chat: 
        chat = services.open_chat(user_id_logged_in, user_id)
        
    return JsonResponse({'room_name': chat.id})
