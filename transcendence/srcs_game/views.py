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
    return JsonResponse({'room_id': game.id})

def room(request, room_id):
    game = Game.objects.filter(pk=int(room_id))
    if not game:   
        raise Http404
    game = game.first()
    return render(request,
                  "game/index.html",
                  context={
                    "room_id": room_id,
                    "leftPlayer": game.leftPlayer.id,
                    "rightPlayer": game.rightPlayer.id})

def users_list(request):
    users = User.objects.all()
    return render(request, 'game/game_list.html', {'users': users})
