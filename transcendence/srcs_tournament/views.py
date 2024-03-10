from django.shortcuts import render, redirect
from srcs_user.models import User
from srcs_user.services import find_one_intra
from srcs_tournament.models import Tournament
from srcs_auth.jwt_token import verify_jwt_token
from django.http import Http404
from srcs_chat.models import Chat
from srcs_message.services import add_message

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
        id_42 = get_user_id_from_cookie(request)
        if id_42 is not None:
            try:
                user = find_one_intra(id_42)
                user_id = user.id
                tournament = Tournament.objects.create()
                tournament.users.add(user_id)
                user_id_bot_chat = Chat.objects.filter(users_on_chat=user_id).filter(users_on_chat=1)
                if user_id_bot_chat.count() > 0:
                    add_message(user_id_bot_chat.first().id, "You created a tournament", user_id)
                return redirect('srcs_tournament:users_list', user_id=user_id)
            except User.DoesNotExist:
                raise Http404("Usuário não encontrado")
            # except Exception as e:
            #     # Lidar com outras exceções
            #     pass
        else:
            return redirect('srcs_auth:intra_login')
            pass
    return render(request, 'tournament/create_tournament.html', {'user_id': -1})

def get_user_id_from_cookie(request):
    cookie_header = request.headers.get('cookie', None)
    
    if cookie_header:
        cookie_str = cookie_header.split("jwt_token=")[1].split(";")[0]
        if cookie_str:
            try:
                payload = verify_jwt_token(cookie_str)
                return payload["id_42"]
            except Exception as e:
                # Lidar com exceções
                pass
    return None

def users_list(request, user_id):
    users = User.objects.all()
    called_players = [int(player_id) for player_id in request.session.get('called_players', [])]
    print(called_players)
    users = [user for user in users if (user.id != user_id and user.id not in called_players)]
    print(users)
    return render(request, 'tournament/users_list.html', {'users': users})
