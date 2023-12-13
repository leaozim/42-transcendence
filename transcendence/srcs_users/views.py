from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import AnonymousUser
from .auth import verify_jwt_token, generate_jwt_token
from .forms import UserCreationForm
import requests
from .models import User

auth_url_intra =  "https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-fec16bce7005bda3749ca50ff01b5f0c8fcf8964b552af66aa05c0dc76a7c485&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Foauth2%2Flogin%2Fredirect&response_type=code"

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "helo"})

@login_required
def get_authenticated_user(request):
    if request.user.is_authenticated:
        return HttpResponse(f'Usuário autenticado: {request.user.username}')
    else:
        return HttpResponse('Usuário não autenticado')
        
def intra_login(request: HttpRequest): 
    return redirect(auth_url_intra)

def intra_login_redirect(request: HttpRequest):
    code = request.GET.get('code')
    user_data = exchange_code(code)
    intra_user = User.objects.filter(id42=user_data['id']).first()
    if not intra_user:
        intra_user = User.objects.create(
            id42=user_data['id'],
            avatar=user_data['url'],
            email=user_data['email'],
            username=user_data['login'],
        )
    
    jwt_token = generate_jwt_token(user_data)
    response = JsonResponse({'token': jwt_token})
    response.set_cookie('jwt_token', jwt_token, httponly=True, samesite='Lax')
    return response


def exchange_code(code: str):
    data = {
        "client_id": "u-s4t2ud-fec16bce7005bda3749ca50ff01b5f0c8fcf8964b552af66aa05c0dc76a7c485",
        "client_secret": "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",
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/oauth2/login/redirect",
        "scope": "identify"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post("https://api.intra.42.fr/oauth/token", data=data, headers=headers)
    credentials = response.json()
    access_token = credentials['access_token']
    response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer %s' % access_token})
    user = response.json()
    return user

@ensure_csrf_cookie
def logout(request):
    for cookie_name, cookie_value in request.COOKIES.items():
        if cookie_name == 'jwt_token':
            response = JsonResponse({'message': 'Logout successful'})
            response.delete_cookie(cookie_name)
            print(f'Nome do cookie: {cookie_name}, Valor do cookie: {cookie_value}')
            return response

    return HttpResponse('Cookies processados com sucesso.')