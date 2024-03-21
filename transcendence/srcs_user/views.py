from typing import Any, Dict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView
from srcs_auth.decorators import two_factor_required
from srcs_user.models import User

from .form import BlockForm


@login_required
@two_factor_required
def test(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"msg": "hello"})


def users_list(request):
    users = User.objects.all()
    return render(
        request,
        "user/usersList.html",
        {"users": users, "caller": "caller_is_user_list"},
    )


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
        blocked_user_id: int = User.objects.get(username=blocked_user_name).pk

        blocked_user = self.request.user.blocked_by.create(
            blocked_by=self.request.user, blocked_user_id=blocked_user_id
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
        blocked_user_name: str = form.cleaned_data.get("blockedUserName")
        blocked_user_id: int = User.objects.get(username=blocked_user_name).pk

        self.request.user.blocked_user.filter(blocked_user_id=blocked_user_id).delete()

        return HttpResponse(content="", status=200)
