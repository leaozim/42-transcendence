from srcs_chat import Message

def add_message(chat_id, content, user_id):
    message = Message.objects.create(
        chat_id=chat_id,
        content=content,
        user=user_id,
    )
    return message 

