from django.contrib.auth.models import AnonymousUser
from srcs_auth.jwt_token import verify_jwt_token, JWTVerificationFailed
from django.urls import reverse
from django.shortcuts import redirect
from django.urls import path
from django.http import HttpResponse
import logging

logging.basicConfig(level=logging.INFO)

class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_routes = [
            reverse('srcs_user:oauth2'),
            reverse('srcs_auth:logout_user'),
        ]

    def __call__(self, request):
        request.user = AnonymousUser()

        if self._is_allowed_route(request.path_info):
            return self._authenticate_user(request)
        return self.get_response(request)

    def _is_allowed_route(self, path_info):
        return path_info in self.allowed_routes

    def _authenticate_user(self, request):
        try:
            jwt_token = request.COOKIES.get('jwt_token', None)
            user = verify_jwt_token(jwt_token)
            logging.info(jwt_token)
            request.user = user
            return self.get_response(request)
        except JWTVerificationFailed:
            return self._handle_verification_failure(request)

    def _handle_verification_failure(self, request):
        if request.path_info in self.allowed_routes:
            request.jwt_redirect_attempted = True  
            return redirect('/')  
