from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404, render, redirect
from srcs_game.forms import GameSettingsForm
from srcs_game.models import DEFAULT_DURATION_MINUTES, MAX_DURATION_MINUTES, MAX_TARGET_SCORE, Game
from srcs_game.services import (
    can_cancel,
    cancel_game,
    create_computer_game,
    create_game,
    open_games_for,
)
from srcs_user.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST
from django.views.generic.list import ListView
from srcs_message.services import add_tournament_message


def _invalid_settings(form):
    return JsonResponse({"error": form.error_message()}, status=400)


@require_POST
@login_required
def create_game_view(request, right_player_id):
    """Challenge another player. The game waits until both are ready."""
    right_player = get_object_or_404(User, id=int(right_player_id))
    left_player = request.user
    form = GameSettingsForm(request.POST)
    if not form.is_valid():
        return _invalid_settings(form)

    game = create_game(left_player, right_player, **form.settings())
    room_url = request.build_absolute_uri(reverse("srcs_game:room", args=[game.id]))
    message = f"{left_player.username} has challenged you to a game: {room_url}"
    add_tournament_message(right_player, message)
    return JsonResponse({'room_id': game.id})

@require_POST
@login_required
def create_computer_game_view(request):
    """Start a single-player game against the computer."""
    form = GameSettingsForm(request.POST)
    wants_json = "application/json" in request.headers.get("Accept", "")
    if not form.is_valid():
        if wants_json:
            return _invalid_settings(form)
        form = GameSettingsForm({})
        form.is_valid()
    game = create_computer_game(request.user, **form.settings())
    if wants_json:
        return JsonResponse({"room_id": game.id})
    return redirect("srcs_game:room", room_id=game.id)


@require_POST
@login_required
def cancel_game_view(request, room_id):
    """Cancel (creator) or decline (opponent) a game that has not started."""
    game = get_object_or_404(Game, pk=room_id)
    try:
        cancel_game(game, request.user)
    except PermissionDenied:
        return JsonResponse({"error": _("This game can no longer be canceled.")}, status=403)
    # Tell whoever is waiting in the game room.
    from srcs_game.consumers import group_name

    async_to_sync(get_channel_layer().group_send)(group_name(game.id), {"type": "game_canceled"})
    return JsonResponse({"canceled": True})


@require_GET
@login_required
def open_games_view(request):
    """The "open games" panel of the home page (reloaded on lobby events)."""
    return render(request, "game/open_games.html", open_games_context(request.user))


def open_games_context(user):
    from srcs_game.consumers import games, group_name

    items = []
    for game in open_games_for(user):
        opponent = game.rightPlayer if game.leftPlayer_id == user.id else game.leftPlayer
        session = games.get(group_name(game.id))
        items.append({
            "game": game,
            "opponent": opponent,
            "in_progress": game.started_at is not None,
            "tournament": game.tournament_id is not None,
            # Challenges are created with the challenger on the left.
            "challenged_me": game.rightPlayer_id == user.id,
            "opponent_in_room": bool(session and session.is_connected(opponent.id)),
            "can_cancel": can_cancel(game, user),
        })
    return {"open_games": items}


def game_texts(game):
    """Texts shown by the game page, in the current language."""
    left_name = game.leftPlayer.username
    right_name = _("Computer") if game.against_computer else game.rightPlayer.username
    return {
        "loading": _("Loading the game…"),
        "leftPlayer": left_name,
        "rightPlayer": right_name,
        "computer": _("Computer"),
        "settings": game.settings_label(),
        "ready": _("Ready"),
        "cancel": _("Cancel game"),
        "statusAbsent": _("not in the room yet"),
        "statusPresent": _("in the room"),
        "statusReady": _("ready"),
        "hintJoin": _("Waiting for %(name)s to join…"),
        "hintPressReady": _("Press Ready when you want to start."),
        "hintWaitReady": _("Waiting for %(name)s to press Ready…"),
        "hintOpponentReady": _("%(name)s is ready. Press Ready to start!"),
        "hintSpectator": _("Waiting for the players to be ready…"),
        "countdown": _("The game starts in %(seconds)s…"),
        "gameOver": _("Game over"),
        "winner": _("The winner is %(name)s!"),
        "draw": _("It's a draw!"),
        "annulled": _("The game was canceled."),
        "playAgain": _("Play again"),
        "backHome": _("Back to home"),
    }


def room(request, room_id):
    game = Game.objects.filter(pk=int(room_id))
    if not game:
        raise Http404
    game = game.first()
    if game.is_finish:
        return redirect('/')
    return render(request,
                  "game/index.html",
                  context={
                    "game": game,
                    "room_id": room_id,
                    "leftPlayer": game.leftPlayer.id,
                    "rightPlayer": game.rightPlayer.id,
                    "vs_computer": game.against_computer,
                    "can_cancel": request.user.is_authenticated and can_cancel(game, request.user),
                    "game_texts": game_texts(game)})


class UserList(LoginRequiredMixin, ListView):
    model = User
    template_name = "game/game_list.html"

    def get_queryset(self):
        # Exclude the current logged-in user and the user with id=1
        queryset = super().get_queryset().exclude(id__in=[self.request.user.id, 1])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            default_minutes=DEFAULT_DURATION_MINUTES,
            max_minutes=MAX_DURATION_MINUTES,
            max_score=MAX_TARGET_SCORE,
        )
        return context
