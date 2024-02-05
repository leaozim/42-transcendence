from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from srcs_auth.decorators import two_factor_required
from srcs_user.models import User

@login_required
@two_factor_required
def test(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})

def users_list(request):
    users = User.objects.all()
    return render(request, 'user/users_list.html', {'users': users})