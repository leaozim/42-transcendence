from srcs_chat.models import Chat
from srcs_user.models import User
from srcs_user.services import get_validated_user
from django.http import Http404
from django.db.models import Count

def get_validated_chat(chat_id):
    try:
        return Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        raise Http404(f"Chat with ID {chat_id} does not exist.")

def get_validated_chat_and_user(chat_id, user_id):    
    chat = get_validated_chat(chat_id)
    user = get_validated_user(user_id)
    
    return chat, user

def is_user_in_chat(chat, user):
    if user in chat.users_on_chat.all():
        return True
    else:
        return False

def block_chat(chat_id, user_id):
    chat, user = get_validated_chat_and_user(chat_id, user_id)
    if is_user_in_chat(chat, user):
        chat.blocked = True
        chat.blocked_by = user
        chat.save()
    return chat

def unblock_chat(chat_id, user_id):
    chat, user = get_validated_chat_and_user(chat_id, user_id)
    if chat.blocked_by != user or not is_user_in_chat(chat, user):
        return chat
    chat.blocked = False
    chat.blocked_by = user
    chat.save()
    return chat
        
def open_chat(user_id_1, user_id_2):
    chat = Chat.objects.create()
    chat.users_on_chat.set([user_id_1, user_id_2])
    chat.save()
    return chat

def find_open_chats(user_id):
    user = get_validated_user(user_id)
    chats = Chat.objects.filter(users_on_chat=user)
    return chats

def get_updated_user_list(id_user, username):
    user_chats = Chat.objects.filter(users_on_chat=id_user)
    users_in_chats = User.objects.filter(users_chats__in=user_chats).distinct()
    user_chats_with_message_count = user_chats.annotate(message_count=Count('message'))

    users_with_messages = []

    for chat in user_chats_with_message_count:
        if chat.message_count > 0:
            users_with_messages.extend(users_in_chats.filter(users_chats=chat))
                        
    users_data = []
    for user in users_with_messages:
    
        user_data = {
            'id': user.id,
            'username': user.username,
            'avatar': user.avatar,
            'corrent_user': username

        }
        users_data.append(user_data)
        
    return (users_data)
