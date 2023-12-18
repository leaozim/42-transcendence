from django.contrib.auth.models import AnonymousUser
from .jwt_token import verify_jwt_token, JWTVerificationFailed
from django.urls import reverse
from django.shortcuts import redirect
from django.urls import path
from django.views.generic.base import TemplateView  
# from srcs_core.views import HomeView
import logging

logger = logging.getLogger(__name__)

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_routes = [
            reverse('srcs_users:home'),
            reverse('srcs_users:logout'),
        ]

    def __call__(self, request):
        print("Middleware __call__ is called")

        is_allowed_route = request.path_info in self.allowed_routes

        if is_allowed_route:
            jwt_token = request.COOKIES.get('jwt_token', None)
            if jwt_token:
                try:
                    user = verify_jwt_token(jwt_token)
                    request.user = user if user else AnonymousUser()
                except JWTVerificationFailed as e:
                    return self.handle_verification_failure(request)

        response = self.get_response(request)
        return response

    def handle_verification_failure(self, request):
        response = None  
        if request.path_info in self.allowed_routes:
            request.jwt_redirect_attempted = True  
            login_url = reverse('login')
            response = redirect(login_url)
        return response
