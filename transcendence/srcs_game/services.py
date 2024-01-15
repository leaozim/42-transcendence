from srcs_game.models import Game
from django.http import Http404
from srcs_user.services import get_validated_user

def create_game(left_player, right_player):
    if left_player == right_player:
        raise Http404("Error when creating game.")
    
    game = Game.objects.create(
        leftPlayer=left_player,
        rightPlayer=right_player,
        leftPlayerScore=0,
        rightPlayerScore=0
    )
    return game
