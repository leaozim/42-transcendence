from django.db import models
from srcs_user.models import User
# from srcs_tournament.models import Tournament
from django.db.models.signals import post_save
from django.dispatch import receiver

class Game(models.Model):
    leftPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_left_player', db_column='left_player')
    rightPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_right_player', db_column='right_player')
    leftPlayerScore = models.IntegerField(db_column='left_player_score')
    rightPlayerScore = models.IntegerField(db_column='right_player_score')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    tournament_id = models.IntegerField(blank=True, null=True, default=None)
    is_finish = models.BooleanField(default=False)

    class Meta:
        db_table = 'game'

@receiver(post_save, sender=Game)
def update_tournament(sender, instance, created, **kwargs):
    if not created:
        if instance.leftPlayerScore > instance.rightPlayerScore:
            instance.winner = instance.leftPlayer
        elif instance.leftPlayerScore < instance.rightPlayerScore:
            instance.winner = instance.rightPlayer
        else:
            pass

        tournament_id = instance.tournament_id
        if tournament_id:
            from srcs_tournament.models import Tournament
            try:
                tournament = Tournament.objects.get(pk=tournament_id)
                tournament.update_state()
            except Tournament.DoesNotExist:
                # Lida com o caso em que o torneio não é encontrado
                pass
