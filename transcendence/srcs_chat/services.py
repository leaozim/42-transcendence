from .models import Chat
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from .models import Chat
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404

def add_admin(chat, user):
    try:
        if not chat.admins.filter(id=user.id).exists():
            chat.admins.add(user)
    except Exception as e:
        print(f"Erro ao adicionar administrador: {e}")

def remove_admin(chat, user):
    try:
        if chat.admins.filter(id=user.id).exists():
            chat.admins.remove(user)
    except Exception as e:
        print(f"Erro ao remover administrador: {e}")

def change_chat_password(chat_id_or_instance, new_password):
    try:
        chat = get_object_or_404(Chat, id=chat_id_or_instance)
        chat.password = new_password.encode('utf-8') # use make_password for hashing
        chat.save()
        return chat
    except Exception as e:
        print(f"Erro ao alterar a senha do chat: {e}")

def mute_user(chat, user):
    try:
        if user not in chat.muteds.all():
            chat.muteds.add(user)
        else:
            print(f"O usuário {user.username} já está mutado.")
    except Exception as e:
        print(f"Erro ao silenciar o usuário: {e}")

def unmute_user(chat, user):
    try:
        if user in chat.muteds.all():
            chat.muteds.remove(user)
        else:
            print(f"O usuário {user.username} já não está desmutado.")
    except Exception as e:
        print(f"Erro ao desmutar o usuário: {e}")

def ban_user(chat, user):
    try:
        if not chat.banneds.filter(id=user.id).exists():
            chat.banneds.add(user)
            print(f"Usuário {user.username} foi banido do chat.")
        else:
            print(f"Usuário {user.username} já está banido do chat.")
    except Exception as e:
        print(f"Erro ao banir o usuário: {e}")


# def change_chat_password(chat_id, new_password):
#     try:
#         chat = Chat.objects.get(id=chat_id)
#         chat.password = new_password.encode('utf-8')
#         chat.save()
#         return chat
#     except Chat.DoesNotExist:
#         raise ValueError(f"Chat with ID {chat_id} does not exist.")
