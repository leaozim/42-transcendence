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

def update_game_result(game_id, score):
    try:
        game = Game.objects.get(pk=game_id)
        game.leftPlayerScore = score[0]
        game.rightPlayerScore = score[1]
        game.save()
    except Game.DoesNotExist:
        raise Http404("Game does not exist")
    
def delete_game(game_id):
    try:
        game = Game.objects.get(pk=game_id)
        game.delete()
    except Game.DoesNotExist:
        raise Http404("Game does not exist")
