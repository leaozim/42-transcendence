from django.db import models
from srcs_user.models import User
from srcs_game.models import Game
from django.utils import timezone

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
