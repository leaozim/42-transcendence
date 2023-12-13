from django.contrib.auth.models import AnonymousUser
from .auth import verify_jwt_token
from .models import User

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        all_cookies = request.COOKIES

        for cookie_name, cookie_value in all_cookies.items():
            if cookie_name == 'jwt_token':
                user = verify_jwt_token(cookie_value)
                if user:
                    request.user = user
                else:
                    request.user = AnonymousUser()

        response = self.get_response(request)

        return response