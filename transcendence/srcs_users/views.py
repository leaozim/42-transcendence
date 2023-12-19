from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from .jwt_token import verify_jwt_token, generate_jwt_token, JWTVerificationFailed
from .forms import UserCreationForm
import os

from .models import User
import requests

from django.contrib.auth.decorators import login_required

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def home(request: HttpRequest) -> JsonResponse:
    return JsonResponse({ "msg":  "hello"})


def get_authenticated_user(request):
    jwt_token = request.COOKIES.get('jwt_token', None)
    
    if jwt_token:   
        try:
            user = verify_jwt_token(jwt_token)
            if user:
                return HttpResponse(f'Usuário autenticado: {user.username}')
        except JWTVerificationFailed as e:
            return HttpResponse(e)

    return HttpResponse('Usuário não autenticado')

def intra_login(request: HttpRequest): 
    return redirect(os.environ.get('AUTH_URL_INTRA'))


def intra_login_redirect(request: HttpRequest):
    code = request.GET.get('code')  
    user_data = exchange_code(code)
    User.objects.create_new_intra_user(user_data)
    jwt_token = generate_jwt_token(user_data)
    user = authenticate(request, jwt_token=jwt_token)
    if user:
        login(request, user)
    response = redirect("/auth/user")
    response.set_cookie('jwt_token', jwt_token, httponly=True, samesite='Lax')
    return response


def exchange_code(code: str):
    data = {
        "client_id": os.environ.get('CLIENT_ID'),
        "client_secret": os.environ.get('CLIENT_SECRET'),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ.get('REDIRECT_URI'),
        "scope": "identify"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post("https://api.intra.42.fr/oauth/token", data=data, headers=headers)
    credentials = response.json()
    access_token = credentials['access_token']
    response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer %s' % access_token})
    user = response.json()
    return user


def logout_user(request):
    response = redirect("/")
    response.delete_cookie("jwt_token")
    logout(request)
    return response