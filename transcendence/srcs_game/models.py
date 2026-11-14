from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext, ngettext
from srcs_user.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import threading

# Game settings chosen when a game is created.
DEFAULT_DURATION_MINUTES = 1
MAX_DURATION_MINUTES = 10
MAX_TARGET_SCORE = 21


class Game(models.Model):
    leftPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_left_player', db_column='left_player')
    rightPlayer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='matches_as_right_player', db_column='right_player')
    leftPlayerScore = models.IntegerField(db_column='left_player_score')
    rightPlayerScore = models.IntegerField(db_column='right_player_score')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    tournament_id = models.IntegerField(blank=True, null=True, default=None)
    is_finish = models.BooleanField(default=False)
    has_started = models.BooleanField(default=False)
    # Length of the match once both players are ready.
    duration_minutes = models.PositiveSmallIntegerField(
        default=DEFAULT_DURATION_MINUTES,
        validators=[MinValueValidator(1), MaxValueValidator(MAX_DURATION_MINUTES)],
    )
    # Points that win the match before the time is up (None: time only).
    target_score = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(MAX_TARGET_SCORE)]
    )
    created_at = models.DateTimeField(default=timezone.now)
    # When play actually began (both players ready); None while waiting.
    started_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'game'

    def settings_label(self):
        """Human-readable settings, e.g. "2 minutes · first to 5 points"."""
        duration = ngettext("%(minutes)s minute", "%(minutes)s minutes", self.duration_minutes) % {
            "minutes": self.duration_minutes
        }
        if self.target_score:
            goal = ngettext("first to %(points)s point", "first to %(points)s points", self.target_score) % {
                "points": self.target_score
            }
        else:
            goal = gettext("no point limit")
        return f"{duration} · {goal}"

    @property
    def against_computer(self):
        from srcs_game.computer import computer_player_id

        return self.rightPlayer_id == computer_player_id()

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
    if not created and instance.has_started is True and instance.is_finish is True:

        tournament_id = instance.tournament_id
        if tournament_id:
            from srcs_tournament.models import Tournament
            try:
                tournament = Tournament.objects.get(pk=tournament_id)
                if tournament.is_active:
                    tournament.update_state()
            except Tournament.DoesNotExist:
                pass

    if created:
        instance.start_connection_timer()


@receiver(post_save, sender=Game)
def refresh_open_games_panels(sender, instance, **kwargs):
    # Tell both players' home pages that their list of open games changed.
    from django.db import transaction
    from srcs_game.notifications import notify_lobby_sync

    players = (instance.leftPlayer_id, instance.rightPlayer_id)
    transaction.on_commit(lambda: notify_lobby_sync(*players))
