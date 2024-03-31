from django.shortcuts import render, redirect
from srcs_game.models import Game
from srcs_game.services import create_game
from srcs_user.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse
from django.views.generic.list import ListView


@login_required
def create_game_view(request, right_player_id):
    right_player = User.objects.get(id=int(right_player_id))
    left_player = request.user

    game = create_game(left_player, right_player)
    return JsonResponse({'room_id': game.id})

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
                    "room_id": room_id,
                    "leftPlayer": game.leftPlayer.id,
                    "rightPlayer": game.rightPlayer.id})


class UserList(LoginRequiredMixin, ListView):
    model = User
    template_name = "game/game_list.html"

    def get_queryset(self):
        # Exclude the current logged-in user and the user with id=1
        queryset = super().get_queryset().exclude(id__in=[self.request.user.id, 1])
        return queryset
