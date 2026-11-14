from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from srcs_game.models import DEFAULT_DURATION_MINUTES, Game
from django.http import Http404
from srcs_user.services import get_validated_user

def create_game(left_player, right_player, duration_minutes=DEFAULT_DURATION_MINUTES, target_score=None):
    if left_player == right_player:
        raise Http404("Error when creating game.")
    
    game = Game.objects.create(
        leftPlayer=left_player,
        rightPlayer=right_player,
        leftPlayerScore=0,
        rightPlayerScore=0,
        duration_minutes=duration_minutes or DEFAULT_DURATION_MINUTES,
        target_score=target_score or None,
    )
    return game

def create_computer_game(player, duration_minutes=DEFAULT_DURATION_MINUTES, target_score=None):
    """Single-player game: ``player`` (left paddle) against the computer."""
    from srcs_game.computer import computer_player_id

    computer = get_validated_user(computer_player_id())
    return create_game(player, computer, duration_minutes, target_score)

def can_cancel(game, user):
    """Players may cancel (or decline) a game that has not started yet.
    Tournament games are managed by the tournament and cannot be canceled."""
    return (
        user.id in (game.leftPlayer_id, game.rightPlayer_id)
        and not game.is_finish
        and game.started_at is None
        and game.tournament_id is None
    )

def cancel_game(game, user):
    if not can_cancel(game, user):
        raise PermissionDenied("This game cannot be canceled.")
    game.is_finish = True
    game.winner = None
    game.save()

def mark_game_started(game_id):
    game = Game.objects.get(pk=game_id)
    if game.started_at is None:
        game.started_at = timezone.now()
        game.save(update_fields=["started_at"])

def finish_game(game_id, score, winner_id):
    game = Game.objects.get(pk=game_id)
    game.leftPlayerScore, game.rightPlayerScore = score
    game.winner_id = winner_id
    game.is_finish = True
    game.save()

def open_games_for(user):
    """Unfinished games of ``user`` against another player, newest first:
    challenges waiting to be accepted and games in progress."""
    from srcs_game.computer import computer_player_id

    now = timezone.now()
    games = (
        Game.objects.filter(Q(leftPlayer=user) | Q(rightPlayer=user), is_finish=False)
        .exclude(rightPlayer_id=computer_player_id())
        .select_related("leftPlayer", "rightPlayer")
        .order_by("-created_at")
    )
    # A started game whose time ran out long ago was abandoned by both players.
    return [
        game for game in games
        if game.started_at is None
        or game.started_at + timedelta(minutes=game.duration_minutes + 1) > now
    ]

def update_game_result(game_id, score):
    try:
        game = Game.objects.get(pk=game_id)
        game.leftPlayerScore = score[0]
        game.rightPlayerScore = score[1]
        game.save()
    except Game.DoesNotExist:
        raise Http404("Game does not exist")
    
def delete_game(game_id):
    try:
        game = Game.objects.get(pk=game_id)
        game.delete()
    except Game.DoesNotExist:
        raise Http404("Game does not exist")
