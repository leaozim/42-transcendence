from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from srcs_auth.decorators import two_factor_required
from srcs_user.models import User


@login_required
@two_factor_required
def test(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"msg": "hello"})


@login_required
@two_factor_required
def get_id(request: HttpRequest, **kwargs) -> JsonResponse:
    return JsonResponse({"id": request.user.id})


def users_list(request):
    users = User.objects.all()
    return render(
        request,
        "user/usersList.html",
        {"users": users, "caller": "caller_is_user_list"},
    )
