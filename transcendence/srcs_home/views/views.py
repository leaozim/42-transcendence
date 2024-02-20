from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View


class IndexView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            user = request.user
            template_name = ("home/index.html")
            context = {
                "user": user
            }
            return render(request, template_name, context)
        else:
            context = {"segment": "index"}
            template = ("index.html")

            return render(request, template, context)
        