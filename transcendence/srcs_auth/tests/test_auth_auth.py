from django.test import TestCase
from srcs_auth.auth import IntraAuthenticationBackend
from srcs_user.tests.factories import UserFactory

class TestAuthAuth(TestCase):
    def test_get_user_on_fail(self):
        intra = IntraAuthenticationBackend()
        user = intra.get_user(999999999)

        self.assertIsNone(user)

    def test_get_user_on_success(self):
        UserFactory()
        intra = IntraAuthenticationBackend()
        user = intra.get_user(1)

        self.assertIsNotNone(user)