from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import TemplateView
from srcs_auth.decorators import two_factor_required
from srcs_chat import services
from srcs_chat.models import Chat
from srcs_core.context_processors import custom_context_processor_chat_data
from srcs_user.models import User


@method_decorator(csrf_protect, name="dispatch")
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "chat/profileVisit.html"

    def get_context_data(self, **kwargs: Any) -> Any:
        username: str
        blocked_user: bool
        context: Dict[str, Any]

        username = self.kwargs["username"]

        blocked_user = (
            self.request.user.blocked_by.filter(
                blocked_by=self.request.user,
                blocked_user_id=User.objects.get(username=username).pk,
            ).count()
            == 1
        )

        context = super().get_context_data(**kwargs)

        context.update({"username": username, "blocked_user": blocked_user})

        return context


class ChatView(View):
    @method_decorator(login_required)
    @method_decorator(two_factor_required)
    def dispatch(self, request, *args, **kwargs):
        if "room_id" in kwargs:
            return self.open_chat(self.request, *args, **kwargs)
        elif "user_id" in kwargs:
            return self.create_or_open_chat(self.request, *args, **kwargs)
        else:
            raise Http404

    def open_chat(self, request, room_id):
        chat = Chat.objects.get(id=int(room_id))

        if not services.is_user_in_chat(chat, request.user):
            raise Http404

        messages = chat.message_set.all().order_by("timestamp")
        sorted_messages = sorted(messages, key=lambda x: x.timestamp)
        other_user = chat.get_other_user(request.user)
        messages_dict = [message.to_dict() for message in sorted_messages]

        context = {
            "chat_id": chat.id,
            "messages": messages_dict,
            "current_user": request.user.username,
            "current_user_id": request.user.id,
            "room_id": room_id,
            "other_user_username": other_user.username,
            "other_user_id": other_user.id,
            "other_user_avatar": other_user.avatar,
        }
        return JsonResponse(context)

    def create_or_open_chat(self, request, user_id):
        user_id_logged_in = request.user.id
        chat = (
            Chat.objects.filter(users_on_chat=user_id_logged_in)
            .filter(users_on_chat=user_id)
            .first()
        )
        if not chat:
            chat = services.open_chat(user_id_logged_in, user_id)
        return JsonResponse({"room_id": chat.id})


class GetUpdatedUserListView(View):
    def get(self, request, *args, **kwargs):
        user_list = custom_context_processor_chat_data(request)
        print(user_list)
        return JsonResponse(user_list)
