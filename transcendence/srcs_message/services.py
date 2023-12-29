from django.http import Http404
from srcs_chat.models import Chat
from srcs_chat.services import get_validated_chat_and_user

from srcs_user.models import User
from srcs_message.models import Message

def add_message(chat_id, content, user_id):
    chat, user = get_validated_chat_and_user(chat_id, user_id)
    
    if len(content) > 500 or not content:
        return 
    if chat.blocked:
        return
    
    message = Message.objects.create(
        chat_id=chat.id,
        content=content,
        user_id=user.id
    )
    
    return message
