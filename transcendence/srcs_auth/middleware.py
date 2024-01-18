from django.contrib.auth import get_user_model
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed
from srcs_user.models import User
from srcs_user.services import find_one_intra
from django.shortcuts import redirect

class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        jwt_token = request.COOKIES.get('jwt_token')

        if jwt_token:
            try:
                user_data = verify_jwt_token(jwt_token)
                try:
                    request.user = User.objects.get(id_42=user_data['id_42'])
                except User.DoesNotExist:
                    redirect('/')
                    return self.get_response(request)
                
            except JWTVerificationFailed as e:
                request.jwt_redirect_attempted = True 
                redirect('srcs_auth:refresh_token') 
                return self.get_response(request)
                
        response = self.get_response(request)
        return response
