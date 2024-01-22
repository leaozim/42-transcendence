from django.test import TestCase
from srcs_auth.auth import IntraAuthenticationBackend, verify_jwt_token
from srcs_user.tests.factories import UserFactory
from mock import patch, Mock
import jwt
from srcs_auth.jwt_token import generate_jwt_token
from srcs_user.tests.factories import UserFactory

class TestAuthAuth(TestCase):
    def setUp(self):
        self.intra = IntraAuthenticationBackend()

    def tearDown(self):
        self.intra = None
        
    def test_get_user_on_fail(self):
        user = self.intra.get_user(999999999)

        self.assertIsNone(user)

    def test_get_user_on_success(self):
        uf = UserFactory()
        user = self.intra.get_user(uf.id_42)

        self.assertIsNotNone(user)

    def test_authenticate_on_failure(self):
        payload = {'id': 81172}

        token = generate_jwt_token(payload)
        self.assertIsNone(self.intra.authenticate(request=None, jwt_token=token, user_intra='cavalinho')) 

    def test_authenticate_on_failure_due_invalid_token(self):
        self.assertRaises(Exception, self.intra.authenticate, 'cavalinho', 'cavalinho')
