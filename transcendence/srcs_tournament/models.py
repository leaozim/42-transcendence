from django.db import models
from srcs_user.models import User
from srcs_game.models import Game
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading
from srcs_message.services import add_message, BOT_ID
from srcs_chat.models import Chat
from srcs_tournament.services import create_a_tournament_game

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
        threading.Timer(60, self.close_tournament_subscription).start()

    def close_tournament_subscription(self):
        self.open_to_subscription = False
        users = self.users.all()
        users_count = users.count()

        if users_count < 4:
            for user in users:
                chat = Chat.objects.filter(users_on_chat=user.id).filter(users_on_chat=BOT_ID)
                add_message(chat.first().id, "num rolô torneio", BOT_ID)
                self.is_active = False
                self.save()
                return

        matchmaking = Matchmaking.objects.create(tournament=self)
        matchmaking.players.set(users)
        matchmaking.save()

        self.save()
        players = list(matchmaking.players.all())
        
        create_a_tournament_game(self, players[0], players[1])
        create_a_tournament_game(self, players[2], players[3])
    
    def update_state(self):
        if len(self.games.all()) < 3 and all(game.is_finish for game in self.games.all()):
            winners = []
            for game in self.games.all():
                if game.leftPlayerScore > game.rightPlayerScore:
                    winners.append(game.leftPlayer)
                else:
                    winners.append(game.rightPlayer)
            
            create_a_tournament_game(self, winners[0], winners[1])
        if len(self.games.all()) == 3 and all(game.is_finish for game in self.games.all()):
            final_game = list(self.games.all())[2]
            if final_game.is_finish and self.is_active == True:
                self.is_active = False
                self.save()
                if final_game.leftPlayerScore > final_game.rightPlayerScore:
                    winner = final_game.leftPlayer
                else:
                    winner = final_game.rightPlayer

                for user in self.users.all():
                    chat = Chat.objects.filter(users_on_chat=user.id).filter(users_on_chat=BOT_ID).first()
                    add_message(chat.id, f"O VENCEDOR FOI {winner.tournament_alias}", BOT_ID)

class Matchmaking(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matchmakings')
    players = models.ManyToManyField(User, related_name='matchmakings')
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=Tournament)
def schedule_tournament_close(sender, instance, created, **kwargs):
    if created:
        instance.schedule_tournament()