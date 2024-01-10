from django.http import HttpRequest, HttpResponse, JsonResponse
from srcs_auth.decorators import login_or_jwt_required

@login_or_jwt_required
def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})
