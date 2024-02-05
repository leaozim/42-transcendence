from django.shortcuts import render
from srcs_chat.models import Chat
from srcs_auth.decorators import two_factor_required
from django.contrib.auth.decorators import login_required
from srcs_chat import services
from srcs_user.models import User
from django.db.models import Count
from django.http import JsonResponse
from django.http import Http404

@login_required
@two_factor_required
def open_chat(request, room_id):
    chat = Chat.objects.get(id=int(room_id))
    if not services.is_user_in_chat(chat, request.user):
        raise Http404
    messages = chat.message_set.all().order_by('timestamp')
    sorted_messages = sorted(messages, key=lambda x: x.timestamp)
    other_user = chat.get_other_user(request.user)
    messages_dict = [message.to_dict() for message in sorted_messages]

    context = {
        'chat': chat,
        'messages': messages_dict,
        'current_user': request.user,
        'room_id': room_id,
        'other_user': other_user,
    }
    
    return render(request, "chat/open_chat.html", context)


def chats_list(request):
    user_chats = Chat.objects.filter(users_on_chat=request.user)

    users_in_chats = User.objects.filter(users_chats__in=user_chats).distinct()
    user_chats_with_message_count = user_chats.annotate(message_count=Count('message'))
    users_with_messages = []

    for chat in user_chats_with_message_count:
        if chat.message_count > 0:
            users_with_messages.extend(users_in_chats.filter(users_chats=chat))

    return render(request, 'chat/list_of_chat_users.html', {'users_in_chats': users_with_messages})

def create_or_open_chat(request, user_id):
    user_id_logged_in = request.user.id 
    
    chat = Chat.objects.filter(users_on_chat=user_id_logged_in).filter(users_on_chat=user_id).first()
    if not chat: 
        chat = services.open_chat(user_id_logged_in, user_id)
        
    return JsonResponse({'room_id': chat.id})

def get_authenticated_user(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    
    return JsonResponse({'error': 'Usuário não autenticado'}, status=401)