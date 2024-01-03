from srcs_chat.models import Chat
from srcs_user.models import User
from srcs_user.services import get_validated_user
from django.http import Http404

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
    user_chats = Chat.objects.filter(users_on_chat=user)
    return user_chats

