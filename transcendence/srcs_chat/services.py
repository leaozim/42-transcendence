from srcs_chat.models import Chat
from srcs_user.models import User
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def block_chat(chat_id):
    chat = Chat.objects.get(id=chat_id)
    chat.blocked = True
    chat.save()
    return chat


def unblock_chat(chat_id):
    chat = Chat.objects.get(id=chat_id)
    chat.blocked = False
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

