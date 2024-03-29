from srcs_chat.services import get_updated_user_list


def custom_context_processor_chat_data(request):
    users_data = get_updated_user_list(request.user.id, request.user.username)
    return users_data
