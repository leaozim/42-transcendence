from django.template import loader
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy


def IndexView(request: HttpRequest):

    if request.user.is_authenticated:

    else :
        context = {"segment": "index"}
        template = loader.get_template("index.html")

        return HttpResponse(template.render(context, request))
