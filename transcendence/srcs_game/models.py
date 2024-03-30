from django.db import models
from srcs_user.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading

class Game(models.Model):
    leftPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_left_player', db_column='left_player')
    rightPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_right_player', db_column='right_player')
    leftPlayerScore = models.IntegerField(db_column='left_player_score')
    rightPlayerScore = models.IntegerField(db_column='right_player_score')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    tournament_id = models.IntegerField(blank=True, null=True, default=None)
    is_finish = models.BooleanField(default=False)
    has_started = models.BooleanField(default=False)

    class Meta:
        db_table = 'game'

    def start_connection_timer(self):
        threading.Timer(45, self.check_connection).start()
    
    def check_connection(self):
        true_instance = Game.objects.get(pk=self.id)
        if true_instance.has_started is False:
            true_instance.is_finish = True
            true_instance.save()
            tournament_id = self.tournament_id
            if tournament_id:
                from srcs_tournament.models import Tournament
                try:
                    tournament = Tournament.objects.get(pk=tournament_id)
                    tournament.update_state()
                except Tournament.DoesNotExist:
                    pass

@receiver(post_save, sender=Game)
def update_tournament(sender, instance, created, **kwargs):
    if instance.is_finish is True:
        return
    if not created and instance.has_started is True and instance.is_finish is True:

        tournament_id = instance.tournament_id
        if tournament_id:
            from srcs_tournament.models import Tournament
            try:
                tournament = Tournament.objects.get(pk=tournament_id)
                tournament.update_state()
            except Tournament.DoesNotExist:
                pass

    if created:
        instance.start_connection_timer()
