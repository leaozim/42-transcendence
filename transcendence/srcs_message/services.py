from srcs_message.models import Message


def get_user_receiving_last_message(user_id):
    last_message = (
        Message.objects.filter(user__id=user_id).order_by("-timestamp").first()
    )

    if last_message:
        chat = last_message.chat
        receiving_user = chat.get_other_user(last_message.user)
        return receiving_user
    else:
        return None
