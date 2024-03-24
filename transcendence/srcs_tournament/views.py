from django.shortcuts import render, redirect
from srcs_user.models import User
from srcs_user.services import find_one_intra
from srcs_tournament.models import Tournament
from srcs_auth.jwt_token import verify_jwt_token
from django.http import Http404
from srcs_chat.models import Chat
from srcs_message.services import add_message
from django.contrib.auth.decorators import login_required

@login_required
def create_tournament(request):
    if request.method == 'POST':
        other_user_id = request.POST.get('user_id')
        called_players = request.session.get('called_players', [])
        if other_user_id and other_user_id not in called_players:
            called_players.append(other_user_id)
            other_user_bot_chat = Chat.objects.filter(users_on_chat=other_user_id).filter(users_on_chat=1)
            if other_user_bot_chat.count() > 0:
                add_message(other_user_bot_chat.first().id, "Abandon hope all ye who enter here, for this place is a tournament.", other_user_id)
            request.session['called_players'] = called_players
        # Pega o ID do usuário do cookie do header
        id = request.user.id
        query =  Tournament.objects.filter(creator__id=id, is_active=True)
        if id is not None and not query.exists():
            try:
                user = User.objects.get(id=id)
                tournament = Tournament.objects.create(creator=user)
                tournament.users.add(user.id)
                user_id_bot_chat = Chat.objects.filter(users_on_chat=id).filter(users_on_chat=1)
                if user_id_bot_chat.count() > 0:
                    add_message(user_id_bot_chat.first().id, "You created a tournament", id)
            except User.DoesNotExist:
                raise Http404("Usuário não encontrado")
            # except Exception as e:
            #     # Lidar com outras exceções
            #     pass
        return redirect('srcs_tournament:users_list', user_id=id)


    return render(request, 'tournament/create_tournament.html', {'user_id': -1})


@login_required
def users_list(request, user_id):
    users = User.objects.all()
    called_players = [int(player_id) for player_id in request.session.get('called_players', [])]
    print(called_players)
    users = [user for user in users if (user.id != user_id and user.id not in called_players)]
    print(users)
    return render(request, 'tournament/users_list.html', {'users': users})
