from django.db import models
from srcs_user.models import User
from srcs_game.models import Game
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
from srcs_message.services import add_message
from srcs_chat.models import Chat

BOT_ID = 1

def get_current_datetime():
    return timezone.now()

class Tournament(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(
        User, 
        related_name='users', 
        blank=True, 
        db_column='users')
    games = models.ManyToManyField(
        Game, 
        related_name='games', 
        blank=True, 
        db_column='games')
    open_to_subscription = models.BooleanField(default=True)
    register_date = models.DateTimeField(default=get_current_datetime)

    def schedule_tournament(self):
        threading.Timer(180, self.close_tournament_subscription).start()

    def close_tournament_subscription(self):
        print(get_current_datetime())
        self.open_to_subscription = False
        users = self.users.all()
        users_count = users.count()

        if users_count < 4:
            for user in users:
                chat = Chat.objects.filter(users_on_chat=user.id).filter(users_on_chat=BOT_ID)
                add_message(chat.first().id, "num rolô torneio", BOT_ID)
        
        first_matchmaking_users = users[:4]
        first_matchmaking = Matchmaking.objects.create(tournament=self)
        first_matchmaking.players.set(first_matchmaking_users)
        first_matchmaking.save()

        matchmackings = [first_matchmaking]

        second_matchmaking_users = users[4:]
        if len(second_matchmaking_users) < 4:
            for user in second_matchmaking_users:
                chat = Chat.objects.filter(users_on_chat=user.id).filter(users_on_chat=BOT_ID)
                add_message(chat.first().id, "num rolô torneio pra você", BOT_ID)
                self.users.remove(user)
        else:
            second_matchmaking = Matchmaking.objects.create(tournament=self)
            second_matchmaking.players.set(second_matchmaking_users)
            second_matchmaking.save()
            matchmackings.append(second_matchmaking)

        self.save()
        for matchmaking in matchmackings:
            players = matchmaking.players.all()
                
            game_1 = Game.objects.create(
            leftPlayer=players[0],
            rightPlayer=players[1],
            leftPlayerScore=0,
            rightPlayerScore=0
            )
            self.games.add(game_1)

            chat = Chat.objects.filter(users_on_chat=game_1.leftPlayer.id).filter(users_on_chat=BOT_ID)
            add_message(chat.first().id, f"Clique aqui para o seu próximo jogo: http://localhost:8000/game/{game_1.id}/", BOT_ID)

            chat = Chat.objects.filter(users_on_chat=game_1.rightPlayer.id).filter(users_on_chat=BOT_ID)
            add_message(chat.first().id, f"Clique aqui para o seu próximo jogo: http://localhost:8000/game/{game_1.id}", BOT_ID)

            game_2 = Game.objects.create(
                leftPlayer=players[2],
                rightPlayer=players[3],
                leftPlayerScore=0,
                rightPlayerScore=0
            )
            self.games.add(game_2)

            chat = Chat.objects.filter(users_on_chat=game_2.leftPlayer.id).filter(users_on_chat=BOT_ID)
            add_message(chat.first().id, f"Clique aqui para o seu próximo jogo: http://localhost:8000/game/{game_2.id}/", BOT_ID)

            chat = Chat.objects.filter(users_on_chat=game_2.rightPlayer.id).filter(users_on_chat=BOT_ID)
            add_message(chat.first().id, f"Clique aqui para o seu próximo jogo: http://localhost:8000/game/{game_2.id}", BOT_ID)


class Matchmaking(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matchmakings')
    players = models.ManyToManyField(User, related_name='matchmakings')
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Tournament)
def schedule_tournament_close(sender, instance, created, **kwargs):
    if created:
        print(get_current_datetime())
        instance.schedule_tournament()