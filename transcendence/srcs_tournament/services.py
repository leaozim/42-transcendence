from srcs_game.models import Game
from srcs_message.services import add_tournament_message

def create_a_tournament_game(tournament, left_player, right_player):
    game = Game.objects.create(
        leftPlayer=left_player,
        rightPlayer=right_player,
        leftPlayerScore=0,
        rightPlayerScore=0,
        tournament_id=tournament.id
        )
    tournament.games.add(game)
    add_tournament_message(left_player.id, f'Click here for your next game against {right_player.tournament_alias}: http://localhost:8000/game/{game.id}/')
    add_tournament_message(right_player.id, f'Click here for your next game against {left_player.tournament_alias}: http://localhost:8000/game/{game.id}/')
