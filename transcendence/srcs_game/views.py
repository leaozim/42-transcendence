from django.shortcuts import render
from srcs_game.models import Game
from django.http import HttpResponseForbidden

def room(request, room_name):
    return render(request, "game/index.html", context={"room_name": room_name})