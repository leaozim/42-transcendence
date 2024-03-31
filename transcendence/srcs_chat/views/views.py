from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView, TemplateView
from srcs_auth.decorators import two_factor_required
from srcs_chat import services
from srcs_chat.form import BlockForm
from srcs_chat.models import Chat
from srcs_core.context_processors import custom_context_processor_chat_data
from srcs_user.models import User


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
            "current_username": request.user.username,
            "current_user_id": request.user.id,
            "current_user_avatat": request.user.avatar,
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
        return JsonResponse(user_list)


@method_decorator(csrf_protect, name="dispatch")
class BlockedFormView(LoginRequiredMixin, FormView):
    template_name = "user/blockUserModal.html"
    form_class = BlockForm
    success_url = "/"

    def render_to_response(
        self, context: Dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        username: str

        username = self.kwargs["username"]

        context.update({"blocked_user": False, "username": username})

        return super().render_to_response(context, **response_kwargs)

    def form_invalid(self, form: BlockForm) -> HttpResponse:
        return HttpResponse(content="User not exist", status=404)

    def form_valid(self, form: BlockForm) -> HttpResponse:
        blocked_user_name: str = form.cleaned_data.get("blockedUserName")
        blocked_user_id: int = User.objects.get(username=blocked_user_name).id

        blocked_user = self.request.user.blocked_by.create(
            blocked_user_id=blocked_user_id
        )

        self.request.user.blocked_by.add(blocked_user)

        return HttpResponse(content="", status=200)


@method_decorator(csrf_protect, name="dispatch")
class UnblockedFormView(LoginRequiredMixin, FormView):
    template_name = "user/blockUserModal.html"
    form_class = BlockForm
    success_url = "/"

    def render_to_response(
        self, context: Dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        username: str

        username = self.kwargs["username"]

        context.update({"blocked_user": True, "username": username})

        return super().render_to_response(context, **response_kwargs)

    def form_invalid(self, form: BlockForm) -> HttpResponse:
        return HttpResponse(content="User not exist", status=404)

    def form_valid(self, form: BlockForm) -> HttpResponse:
        blocked_user_id: int
        unblocked_user_name: str

        unblocked_user_name = form.cleaned_data.get("blockedUserName")
        blocked_user_id = User.objects.get(username=unblocked_user_name).id

        self.request.user.blocked_by.filter(blocked_user_id=blocked_user_id).delete()

        return HttpResponse(content="", status=200)


@method_decorator(csrf_protect, name="dispatch")
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "chat/profileVisit.html"

    def get_context_data(self, **kwargs: Any) -> Any:
        username: str
        avatar: str
        blocked_user: bool
        context: Dict[str, Any]

        username = self.kwargs["username"]
        avatar = User.objects.get(username=username).avatar

        blocked_user = (
            self.request.user.blocked_by.filter(
                blocked_user_id=User.objects.get(username=username).id
            ).count()
            == 1
        )

        context = super().get_context_data(**kwargs)

        context.update({"username": username, "avatar": avatar, "blocked_user": blocked_user})

        return context

def is_chat_blocked(request, chat_id):
    return JsonResponse({'blocked': services.is_chat_blocked(chat_id)})