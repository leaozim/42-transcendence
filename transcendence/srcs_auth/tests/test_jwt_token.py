from django.test import TestCase
from srcs_auth.jwt_token import generate_jwt_token, verify_jwt_token
from srcs_user.tests.factories import UserFactory
from mock import patch, Mock
import jwt

class TestJwtToken(TestCase):
    def test_generate_jwt_token(self):
        user = UserFactory()
        test_id_42 = user.id_42

        token = generate_jwt_token({'id': test_id_42})
        result = verify_jwt_token(token)
        
        payload_user_id = result.get('id_42')

        self.assertEqual(user.id_42, payload_user_id)
