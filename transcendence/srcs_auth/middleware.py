from django.contrib.auth import get_user_model
from srcs_auth.jwt_token import verify_jwt_token
from srcs_user.models import User
from srcs_user.services import find_one_intra

class CustomAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        jwt_token = request.COOKIES.get('jwt_token')

        if jwt_token:
            user_data = verify_jwt_token(jwt_token)
            if user_data:   
                user = find_one_intra(user_data['id_42'])
                request.user = user
                
        response = self.get_response(request)
        return response
