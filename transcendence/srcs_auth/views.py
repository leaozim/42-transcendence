from django.shortcuts import render
from srcs_auth.jwt_token import verify_jwt_token, generate_jwt_token, JWTVerificationFailed
from django.contrib.auth import authenticate, login, logout
from srcs_user.models import User
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import redirect
import os
from srcs_auth.services import exchange_code
from srcs_auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.urls import reverse
from django.views import View
from srcs_auth.auth import IntraAuthenticationBackend
from django_otp.decorators import otp_required

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'account/signup.html'

def get_authenticated_user(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})

    return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

def intra_login(request: HttpRequest): 
    return redirect(os.environ.get('AUTH_URL_INTRA'))

# @otp_required
def intra_login_redirect(request: HttpRequest):
    code = request.GET.get('code')  
    user_intra = exchange_code(code)
    jwt_token = generate_jwt_token(user_intra)
    user = IntraAuthenticationBackend().authenticate(request, jwt_token=jwt_token, user_intra=user_intra)
    
    if user:
        login(request, user, 'srcs_auth.auth.IntraAuthenticationBackend')

    response = redirect("/auth/user") #alterar o retirecionamento para o two-factor
    response.set_cookie('jwt_token', jwt_token, httponly=True, samesite='Lax')
    return response

def logout_user(request):
    response = redirect("/")
    response.delete_cookie("jwt_token")
    logout(request)
    return response

def refresh_token(request):
    jwt_token = request.COOKIES.get('jwt_token')

    if jwt_token:
        try:
            user_data = verify_jwt_token(jwt_token)
            new_jwt_token = generate_jwt_token(user_data)
            response = JsonResponse({'jwt_token': new_jwt_token})
            response.set_cookie('jwt_token', new_jwt_token, httponly=True, samesite='Lax')
            return response
        except JWTVerificationFailed:
            pass
    return JsonResponse({'error': 'Erro ao atualizar o token'}, status=400)

def test_form_view(request):
    return render(request, 'registration/test_form.html')