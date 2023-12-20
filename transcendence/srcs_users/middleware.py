from django.contrib.auth.models import AnonymousUser
from .jwt_token import verify_jwt_token, JWTVerificationFailed
from django.urls import reverse
from django.shortcuts import redirect
from django.urls import path


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_routes = [
            reverse('srcs_users:oauth2'),
            reverse('srcs_users:logout_user'),
        ]

    def __call__(self, request):
        print("Middleware __call__ is called")

        request.user = AnonymousUser()
        is_allowed_route = request.path_info in self.allowed_routes 

        if is_allowed_route:
            jwt_token = request.COOKIES.get('jwt_token', None)
            if jwt_token:
                try:
                    print( "aaaaaaaaaaaa")
                    user = verify_jwt_token(jwt_token)
                    request.user = user
                except JWTVerificationFailed as e:
                    print( "bbbbbbbbbbb")
                    return self.handle_verification_failure(request)
            else:
                return self.handle_verification_failure(request)
        
        response = self.get_response(request)
        return response

    def handle_verification_failure(self, request):
        if request.path_info in self.allowed_routes:
            request.jwt_redirect_attempted = True  
            return redirect('/')  
        return None
