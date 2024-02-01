
from django.test import RequestFactory, TestCase
from django.urls import reverse
from srcs_auth.jwt_token import generate_jwt_token
from srcs_auth.middleware import CustomAuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect, HttpResponseRedirect
from srcs_user.tests.factories import UserFactory
from django.http import HttpResponse

class CustomAuthenticationMiddlewareTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CustomAuthenticationMiddleware(lambda x: HttpResponse())

    def test_verify_jwt_valid_token(self):
        user = UserFactory()
        jwt_token = generate_jwt_token({'id': user.id_42})
        
        request = self.factory.get(reverse('srcs_auth:signup'))  
        request.COOKIES['jwt_token'] = jwt_token
        self.middleware.verify_jwt(request)
        self.assertEqual(request.user, user)

    def test_verify_jwt_invalid_token(self):
        jwt_token = 'your_invalid_jwt_token_here'
        
        request = self.factory.get(reverse('srcs_auth:signup'))  
        request.COOKIES['jwt_token'] = jwt_token
        response = self.middleware.verify_jwt(request)
        
        self.assertEqual(request.user, AnonymousUser())
        self.assertEqual(response.status_code, 401)
        
    def test_verify_jwt_not_user(self):
        jwt_token = generate_jwt_token({'id': 66666})
        
        request = self.factory.get(reverse('srcs_auth:signup'))  
        request.COOKIES['jwt_token'] = jwt_token
        self.middleware.verify_jwt(request)
        self.assertEqual(request.user, AnonymousUser())

    def test_verify_two_factor_auth_not_authenticated(self):
        user = UserFactory()
        request = self.factory.get(reverse('srcs_auth:signup')) 
        request.COOKIES['two_factor'] = True
        request.user = user
        request.user.is_2f_active = True
        self.client.force_login(user)

        response = self.middleware.verify_two_factor_auth(request)

        self.assertIsNotNone(response)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response.url, reverse('home'))


        
    def test_verify_two_factor_auth_authenticated_without_2fa(self):
        user = UserFactory()
        
        # Crie um objeto de requisição simulado
        request = self.factory.get(reverse('srcs_auth:signup'))  # Substitua 'your_view_name' pela sua view real
        request.COOKIES['two_factor'] = None
        request.user = user
        request.user.is_2f_active = True
        request.user = user

        response = self.middleware.verify_two_factor_auth(request)

        self.assertIsNotNone(response)
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 401)

