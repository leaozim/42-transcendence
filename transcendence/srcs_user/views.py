from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})
