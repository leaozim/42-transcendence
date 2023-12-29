from django.test import TestCase
from srcs_auth.auth import IntraAuthenticationBackend
from srcs_user.tests.factories import UserFactory
from mock import patch, Mock
from srcs_auth.jwt_token import verify_jwt_token

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
        user = self.intra.get_user(uf.id42)

        self.assertIsNotNone(user)

    def test_authenticate_on_failure(self):
        self.assertIsNone(self.intra.authenticate('cavalinho'))

    @patch('srcs_auth.tests.test_auth_auth.verify_jwt_token')
    def test_authenticate_on_success(self, mock_verify_jwt_token):
        mock_verify_jwt_token.return_value = 'cavalinho'
        self.assertEqual('cavalinho', IntraAuthenticationBackend().authenticate('cavalinho', 'ao vento'))
