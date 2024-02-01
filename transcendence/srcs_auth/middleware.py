from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.shortcuts import redirect
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed
from srcs_user.models import User

class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.verify_jwt(request)
        self.verify_two_factor_auth(request)

        response = self.get_response(request)
        return response

    def verify_jwt(self, request):
        jwt_token = request.COOKIES.get('jwt_token')

        if jwt_token:
            try:
                user_data = verify_jwt_token(jwt_token)
                try:
                    request.user = User.objects.get(id_42=user_data['id_42'])
                except User.DoesNotExist:
                    request.user = AnonymousUser()
                    redirect('home')
                    return HttpResponse(status=401)  
                
            except JWTVerificationFailed as e:
                request.user = AnonymousUser()
                request.jwt_redirect_attempted = True 
                redirect('srcs_auth:refresh_token') 
                return HttpResponse(status=401)  

    def verify_two_factor_auth(self, request):
        if request.user.is_authenticated and request.user.is_2f_active:
            
            is_two_factor_authenticated =  request.COOKIES.get('two_factor')
            if not is_two_factor_authenticated:
                redirect('srcs_auth:validate_token_2f')
                return HttpResponse(status=401) 
        return redirect('home')




