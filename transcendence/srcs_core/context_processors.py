from srcs_chat.services import get_updated_user_list
from django.http import HttpResponse as HttpResponse, JsonResponse, Http404, HttpResponse

def custom_context_processor_chat_data(request):
    users_data = get_updated_user_list(request.user.id, request.user.username)
    return {'users_in_chats': users_data}

