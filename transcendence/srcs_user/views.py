from django.http import HttpRequest, HttpResponse, JsonResponse

def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})
