from django.http import HttpResponse

def index(_):
    return HttpResponse("Olá")
