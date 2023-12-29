from srcs_chat.models import Chat
from srcs_user.models import User
from django.http import Http404


def get_validated_chat_and_user(chat_id, user_id):    
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        raise Http404(f"Chat with ID {chat_id} does not exist.")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise Http404(f"User with ID {user_id} does not exist.")
    
    return chat, user


def block_chat(chat_id, user_id):
    chat, user = get_validated_chat_and_user(chat_id, user_id)
    chat.blocked = True
    chat.blocked_by = user
    chat.save()
    return chat


def unblock_chat(chat_id, user_id):
    chat, user = get_validated_chat_and_user(chat_id, user_id)
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
   
    user = User.objects.get(id=user_id) 
    user_chats = Chat.objects.filter(users_on_chat=user)

    return user_chats

