import json
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from srcs_auth.jwt_token import generate_jwt_token, JWTVerificationFailed, verify_jwt_token
from srcs_auth.middleware import JWTAuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser


class JWTAuthenticationMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.allowed_route = reverse('auth/user/')
        self.not_allowed_route = reverse('oauth2/logout/')
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_allowed_route_without_token(self):
        request = self.factory.get(self.allowed_route)
        middleware = JWTAuthenticationMiddleware(lambda r: None)
        response = middleware(request)
        self.assertEqual(response, None)
        self.assertEqual(request.user, AnonymousUser())

    def test_allowed_route_with_valid_token(self):
        jwt_token = generate_jwt_token(self.user)
        request = self.factory.get(self.allowed_route, HTTP_COOKIE=f'jwt_token={jwt_token}')
        middleware = JWTAuthenticationMiddleware(lambda r: None)
        response = middleware(request)
        self.assertEqual(response, None)
        self.assertEqual(request.user, self.user)

    def test_allowed_route_with_invalid_token(self):
        request = self.factory.get(self.allowed_route, HTTP_COOKIE='jwt_token=invalid_token')
        middleware = JWTAuthenticationMiddleware(lambda r: None)
        with self.assertRaises(JWTVerificationFailed):
            middleware(request)

        self.assertEqual(request.user, AnonymousUser())

    def test_not_allowed_route(self):
        request = self.factory.get(self.not_allowed_route)
        middleware = JWTAuthenticationMiddleware(lambda r: None)
        response = middleware(request)
        self.assertEqual(response, None)
        self.assertEqual(request.user, AnonymousUser())
