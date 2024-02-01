from django.test import TestCase
from unittest.mock import patch
from srcs_auth.services import TOTPService
from django_otp.plugins.otp_totp.models import TOTPDevice
from srcs_user.tests.factories import UserFactory
from srcs_auth.tests.factories import TOTPDeviceFactory
import pyotp

class TOTPServiceTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_create_totp_code(self):
        totp_service = TOTPService()
        qr_code, totp_code = totp_service.create_totp_code(self.user)

        self.assertIsNotNone(qr_code)
        self.assertIsNotNone(totp_code)
        self.assertTrue(self.user.is_2f_active)

    def test_verify_totp_token(self):
        totp_service = TOTPService()
        qr_code, totp_code = totp_service.create_totp_code(self.user)
        token =  pyotp.TOTP(totp_code).now()
        result = totp_service.verify_totp_token(self.user, token)
        self.assertTrue(result)

    def test_delete_totp_devices(self):
        totp_service = TOTPService()
        qr_code, totp_code = totp_service.create_totp_code(self.user)
        
        result_before_deletion = TOTPDevice.objects.filter(user=self.user).exists()

        totp_service.delete_totp_devices(self.user)

        result_after_deletion = TOTPDevice.objects.filter(user=self.user).exists()

        self.assertTrue(result_before_deletion)
        self.assertFalse(result_after_deletion)
        self.assertFalse(self.user.is_2f_active)

    # Add more test cases for other functions as needed