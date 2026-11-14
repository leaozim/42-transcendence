from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_protect
from django.views.generic.list import ListView
from srcs_message.services import add_tournament_message
from srcs_tournament.models import Tournament
from srcs_user.models import User


@login_required
@csrf_protect
def create_tournament(request):

    id = request.user.id
    if request.method == "POST":
        query = Tournament.objects.filter(creator__id=id, is_active=True)
        if id is not None and not query.exists():
            try:

                if User.objects.count() < 5:
                    return HttpResponse(
                        format_html("<p>{}</p>", _("A tournament needs at least 4 players. Wait for more users to join.")),
                        status=200,
                    )

                if Tournament.objects.filter(creator__id=id).count() < 1:
                    user = User.objects.get(id=id)
                    tournament = Tournament.objects.create(creator=user)
                    tournament.users.add(user.id)
                    add_tournament_message(
                        id,
                        'You created a tournament. It will start when 3 more players join (invite them... duh).<br> <span class="clickable-link" onClick="openOnModal(\'/tournament-alias/\');">Click here to change your tournament nickname</span>',
                    )
                else:
                    return HttpResponse(
                        format_html("<p>{}</p>", _("With the free subscription, you can only create one tournament.")),
                        status=200,
                    )
            except User.DoesNotExist:
                raise Http404("User not found")
        else:
            tournament_id = query.last().id
            if query.last().open_to_subscription is False:
                add_tournament_message(id, "The tournament registration deadline has passed.")
                return HttpResponse(
                    format_html("<p>{}</p>", _("With the free subscription, you can only create one tournament.")),
                    status=200,
                )
            other_user_id = request.POST.get("user_id")
            called_players = request.session.get("called_players", [])
            if other_user_id and other_user_id not in called_players:
                called_players.append(other_user_id)
                add_tournament_message(
                    other_user_id,
                    f'You were invited to tournament #{tournament_id}.<br> <span class="clickable-link" onClick="openOnModal(\'/tournament-alias/\');">Click here to change your nickname</span> <br> <span class="clickable-link" onClick="dontOpenOnModal(\'/tournament_player_invite/{tournament_id}/{other_user_id}/\')">Click here to accept</span>',
                )
                request.session["called_players"] = called_players
        return redirect("srcs_tournament:users_list", user_id=id)
    return render(request, "tournament/create_tournament.html", {"user_id": 1})


@login_required
def users_list(request, user_id):
    users = User.objects.all()
    called_players = [
        int(player_id) for player_id in request.session.get("called_players", [])
    ]
    users = [
        user
        for user in users
        if (user.id != user_id and user.id != 1 and user.id not in called_players)
    ]
    if not len(users):
        return HttpResponse(
            format_html("<p>{}</p>", _("There are no more players to invite.")),
            status=200,
        )

    return render(request, "tournament/users_list.html", {"users": users})


@login_required
def user_accept(request, user_id, user_accept_id):
    tournament = Tournament.objects.get(pk=user_id)
    if tournament.open_to_subscription == False:
        add_tournament_message(
            request.user.id, "The tournament registration deadline has passed."
        )
        return redirect("/")

    user_accept = User.objects.get(pk=user_accept_id)
    tournament.users.add(user_accept)

    users = tournament.users.all()
    users_count = users.count()

    if users_count == 4:
        tournament.open_to_subscription = False
        tournament.save()
        for user in users:
            add_tournament_message(
                user.id,
                f"{user_accept.tournament_alias} has joined tournament #{tournament.id}. The tournament will start soon.",
            )
        return redirect("/")

    missing = 4 - users_count
    for user in users:
        add_tournament_message(
            user.id,
            f"{user_accept.tournament_alias} has joined tournament #{tournament.id}. "
            f"Waiting for {missing} more {'player' if missing == 1 else 'players'} before it starts.",
        )
    return redirect("/")


@login_required
def create_tournament_alias(request):
    template = "tournament/create_tournament_alias.html"
    if request.method == "POST":
        alias = request.POST.get("name")
        user = User.objects.get(id=request.user.id)
        user.tournament_alias = alias
        user.save()
        context = {"flag_tournament_created": True}
        return render(request, template, context)

    else:
        return render(request, template)


class UserList(ListView):
    model = User
    template_name = "tournament/tournament_list.html"

    def user_list(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
