from django.shortcuts import render
from srcs_game.models import Game
from srcs_game.services import create_game
from srcs_user.models import User
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import JsonResponse


@login_required
def create_game_view(request, right_player_id):
    right_player = User.objects.get(id=int(right_player_id))
    left_player = request.user 
    
    game = create_game(left_player, right_player)
    return JsonResponse({'room_name': game.id})

def room(request, room_name):
    game = Game.objects.filter(pk=int(room_name))
    if not game:   
        raise Http404
    return render(request, "game/index.html", context={"room_name": room_name})

