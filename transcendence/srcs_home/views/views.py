from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View
from srcs_auth.services import AUTHENTICATOR_APPS
from srcs_auth.views import render_login_page
from srcs_game.views import open_games_context


class IndexView(View):

    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            user = request.user
            template_name = ("home/index.html")
            context = {
                "user": user,
                "authenticator_apps": AUTHENTICATOR_APPS,
                **open_games_context(user),
            }
            return render(request, template_name, context)
        else:
            return render_login_page(request)
        