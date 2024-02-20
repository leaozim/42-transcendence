from srcs_chat.models import Chat
from srcs_user.models import User 
from django.db.models import Count

def custom_context_processor_chat_data(request):
    user_chats = Chat.objects.filter(users_on_chat=request.user.id)
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

        }
        users_data.append(user_data)
    return {'users_in_chats': users_data}
