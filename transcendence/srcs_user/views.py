from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from srcs_auth.decorators import two_factor_required

@login_required
@two_factor_required
def test(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})
