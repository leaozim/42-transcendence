from django.db import models
from pong_users.models import User

class Match(models.Model):
    leftPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_left_player', db_column='left_player')
    rightPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_right_player', db_column='right_player')
    leftPlayerScore = models.IntegerField(db_column='left_player_score')
    rightPlayerScore = models.IntegerField(db_column='right_player_score')
    date = models.DateTimeField()

    class Meta:
        db_table = 'match'
