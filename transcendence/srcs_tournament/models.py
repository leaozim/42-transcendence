from django.db import models
from srcs_users.models import User
from srcs_game.models import Game

class Tournament(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tournament'