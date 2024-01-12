from django.http import HttpRequest, HttpResponse, JsonResponse
# from srcs_auth.decorators import login_or_jwt_required
from django.contrib.auth.decorators import login_required

@login_required
def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})
