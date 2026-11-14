from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from srcs_auth.decorators import two_factor_required
from srcs_user.forms import AvatarUploadForm
from srcs_user.models import User, BlockedUser
from srcs_user.services import save_avatar


@login_required
@two_factor_required
def test(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"msg": "hello"})


@login_required
@two_factor_required
def get_id(request: HttpRequest, **kwargs) -> JsonResponse:
    return JsonResponse({"id": request.user.id})


@require_POST
@login_required
@two_factor_required
def upload_avatar(request: HttpRequest) -> JsonResponse:
    form = AvatarUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({"error": " ".join(form.errors["avatar"])}, status=400)
    return JsonResponse({"avatar": save_avatar(request.user, form.cleaned_data["avatar"])})


def users_list(request):
    users = User.objects.all()
    return render(
        request,
        "user/usersList.html",
        {"users": users, "caller": "caller_is_user_list"},
    )

def check_blocked_user(request):
    blocked_by_id = request.GET.get('blocked_by_id')
    blocked_user_id = request.GET.get('blocked_user_id')
    
    blocked_user = BlockedUser.objects.filter(
        blocked_by_id=blocked_by_id,
        blocked_user_id=blocked_user_id
    ).first()

    if blocked_user:
        blocked = True
    else:
        blocked = False
        
    return JsonResponse({'blocked': blocked})