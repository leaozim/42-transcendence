from srcs_game.models import Game
from srcs_chat.models import Chat
from srcs_message.services import add_message

BOT_ID = 1

def create_a_tournament_game(tournament, left_player, right_player):
    game = Game.objects.create(
        leftPlayer=left_player,
        rightPlayer=right_player,
        leftPlayerScore=0,
        rightPlayerScore=0,
        tournament_id=tournament.id
        )
    tournament.games.add(game)

    chat = Chat.objects.filter(users_on_chat=game.leftPlayer.id).filter(users_on_chat=BOT_ID)
    add_message(chat.first().id, f"Clique aqui para o seu próximo jogo: http://localhost:8000/game/{game.id}/", BOT_ID)

    chat = Chat.objects.filter(users_on_chat=game.rightPlayer.id).filter(users_on_chat=BOT_ID)
    add_message(chat.first().id, f"Clique aqui para o seu próximo jogo: http://localhost:8000/game/{game.id}", BOT_ID)