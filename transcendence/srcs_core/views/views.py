from django.template import loader
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy


def IndexView(request: HttpRequest):
    context = {"segment": "index"}
    template = loader.get_template("index.html")

    return HttpResponse(template.render(context, request))
