from django.shortcuts import render, redirect
from srcs_user.models import User
from srcs_tournament.models import Tournament
from django.http import Http404
from srcs_chat.models import Chat
from srcs_message.services import add_message
from django.contrib.auth.decorators import login_required

@login_required
def create_tournament(request):
    
    id = request.user.id
    url = request.META["HTTP_HOST"]
    protocol = "https" if request.is_secure() else "http"
    if request.method == 'POST':
        query =  Tournament.objects.filter(creator__id=id, is_active=True)
        if id is not None and not query.exists():
            try:
                user = User.objects.get(id=id)
                tournament = Tournament.objects.create(creator=user)
                tournament.users.add(user.id)
                user_id_bot_chat = Chat.objects.filter(users_on_chat=id).filter(users_on_chat=1)
                if user_id_bot_chat.count() > 0:
                    add_message(user_id_bot_chat.first().id, "You created a tournament. Wait for 3 more players to start.", id)
            except User.DoesNotExist:
                raise Http404("Usuário não encontrado")
        else:
            tournament_id = query.last().id
            if (query.last().open_to_subscription == False):
                return redirect('/')
            other_user_id = request.POST.get('user_id')
            called_players = request.session.get('called_players', [])
            if other_user_id and other_user_id not in called_players:
                called_players.append(other_user_id)
                other_user_bot_chat = Chat.objects.filter(users_on_chat=other_user_id).filter(users_on_chat=1)
                if other_user_bot_chat.count() > 0:
                    add_message(other_user_bot_chat.first().id, f"You was invited to the tournament #{tournament_id}. Click here to accept: {protocol}://{url}/tournament_player_invite/{tournament_id}/{other_user_id}", other_user_id)
                request.session['called_players'] = called_players
        return redirect('srcs_tournament:users_list', user_id=id)
    return render(request, 'tournament/create_tournament.html', {'user_id': -1})


@login_required
def users_list(request, user_id):
    users = User.objects.all()
    called_players = [int(player_id) for player_id in request.session.get('called_players', [])]
    users = [user for user in users if (user.id != user_id and user.id not in called_players)]
    return render(request, 'tournament/users_list.html', {'users': users})


@login_required
def user_accept(request, user_id, user_accept_id):
    tournament = Tournament.objects.get(pk=user_id)
    if tournament.open_to_subscription == False:
        add_message(Chat.objects.filter(users_on_chat=request.user.id).filter(users_on_chat=1).first().id, "Prazo para inscrição do torneio encerrado", 1)
        return redirect('/')
    
    user_accept = User.objects.get(pk=user_accept_id)
    tournament.users.add(user_accept)
    
    users = tournament.users.all()
    users_count = users.count()
    
    if users_count == 4:
        tournament.open_to_subscription = False
        tournament.save()
        
    for user in users:
        other_user_bot_chat = Chat.objects.filter(users_on_chat=user.id).filter(users_on_chat=1)
        add_message(other_user_bot_chat.first().id,  f"{user_accept.username} have joined the tournament #{tournament.id}. Wait for {4 - users_count} more players to start." , 1)

    return redirect('/')
