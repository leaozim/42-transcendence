from django.shortcuts import render
from srcs_auth.jwt_token import verify_jwt_token, generate_jwt_token, JWTVerificationFailed
from django.contrib.auth import authenticate, login, logout
from srcs_user.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
import os
from srcs_auth.services import exchange_code
from srcs_auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
# Create your views here.

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def get_authenticated_user(request):
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username})
    jwt_token = request.COOKIES.get('jwt_token', None)
    if jwt_token:
        try:
            user = verify_jwt_token(jwt_token)
            if user:
                return JsonResponse({'username': user.username})
        except JWTVerificationFailed as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

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

def logout_user(request):
    response = redirect("/")
    response.delete_cookie("jwt_token")
    logout(request)
    return response