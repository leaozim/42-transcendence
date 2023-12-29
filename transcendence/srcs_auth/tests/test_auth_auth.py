from django.test import TestCase
from srcs_auth.auth import IntraAuthenticationBackend
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
        user = self.intra.get_user(uf.id42)

        self.assertIsNotNone(user)

    def test_authenticate_on_failure(self):
        self.assertIsNone(self.intra.authenticate('cavalinho'))
