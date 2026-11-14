import time

import pyotp
from django.contrib.auth import SESSION_KEY
from django.test import TestCase
from django.urls import reverse
from django_otp import DEVICE_ID_SESSION_KEY
from django_otp.plugins.otp_totp.models import TOTPDevice
from srcs_auth import views as auth_views
from srcs_auth.services import TOTPService
from srcs_user.models import User

PASSWORD = "c0rrect-Horse-battery"
# The first configured backend (42 intra) looks users up by id_42, so sessions
# for password users must name the model backend explicitly.
MODEL_BACKEND = "django.contrib.auth.backends.ModelBackend"


def current_code(device):
    secret = TOTPService().parse_totp_secret(device.config_url)
    return pyotp.TOTP(secret).now()


class PasswordLoginTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("player", "player@example.com", PASSWORD)
        self.login_url = reverse("srcs_auth:login-django")
        self.verify_url = reverse("srcs_auth:login-2fa")
        self.home_url = reverse("srcs_home:home")

    def enable_2fa(self, app="authy"):
        TOTPService().create_totp_code(self.user, app)
        device = TOTPDevice.objects.get(user=self.user)
        device.confirmed = True
        device.save()
        self.user.is_2f_active = True
        self.user.save()
        return device

    def post_password(self, password=PASSWORD, **extra):
        return self.client.post(
            self.login_url, {"username": "player", "password": password, **extra}
        )

    def assertLoggedIn(self):
        self.assertEqual(int(self.client.session[SESSION_KEY]), self.user.pk)

    def assertNotLoggedIn(self):
        self.assertNotIn(SESSION_KEY, self.client.session)

    # --- landing page ---------------------------------------------------------

    def test_landing_page_has_login_form_and_no_42_button(self):
        response = self.client.get(self.home_url)

        self.assertContains(response, f'action="{self.login_url}"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, reverse("srcs_auth:signup"))
        self.assertNotContains(response, reverse("srcs_auth:intra_login"))

    def test_login_required_pages_redirect_to_landing_page(self):
        response = self.client.get(reverse("srcs_user:me"))

        self.assertRedirects(
            response, f"{self.home_url}?next=/user/", fetch_redirect_response=False
        )

    # --- password step --------------------------------------------------------

    def test_wrong_password_shows_error(self):
        response = self.post_password("wrong")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alert-message error")
        self.assertNotLoggedIn()

    def test_login_without_2fa_logs_in_directly(self):
        response = self.post_password()

        self.assertRedirects(response, self.home_url, fetch_redirect_response=False)
        self.assertLoggedIn()
        # A JWT from a previous 42 login must not override the new session.
        self.assertEqual(response.cookies["jwt_token"].value, "")

    def test_unconfirmed_device_does_not_require_code(self):
        TOTPService().create_totp_code(self.user, "google")

        response = self.post_password()

        self.assertRedirects(response, self.home_url, fetch_redirect_response=False)
        self.assertLoggedIn()

    def test_next_is_followed_and_unsafe_next_ignored(self):
        response = self.post_password(next="/user/")
        self.assertRedirects(response, "/user/", fetch_redirect_response=False)

        self.client.logout()
        response = self.post_password(next="https://evil.example/")
        self.assertRedirects(response, self.home_url, fetch_redirect_response=False)

    def test_authenticated_user_visiting_login_is_redirected(self):
        self.client.force_login(self.user, backend=MODEL_BACKEND)

        response = self.client.get(self.login_url)

        self.assertRedirects(response, self.home_url, fetch_redirect_response=False)

    # --- two-factor step ------------------------------------------------------

    def test_password_alone_is_not_enough_with_2fa(self):
        self.enable_2fa()

        response = self.post_password()

        self.assertRedirects(response, self.verify_url, fetch_redirect_response=False)
        self.assertNotLoggedIn()
        # The home page still shows the login form.
        self.assertContains(self.client.get(self.home_url), 'name="password"')

    def test_code_page_names_the_chosen_app(self):
        self.enable_2fa("authy")
        self.post_password()

        response = self.client.get(self.verify_url)

        self.assertContains(response, "<strong>Authy</strong>")
        self.assertContains(response, 'autocomplete="one-time-code"')

    def test_wrong_code_is_rejected(self):
        device = self.enable_2fa()
        self.post_password()
        wrong = str((int(current_code(device)) + 1) % 1000000).zfill(6)

        response = self.client.post(self.verify_url, {"token": wrong})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid code")
        self.assertNotLoggedIn()

    def test_malformed_code_is_rejected(self):
        self.enable_2fa()
        self.post_password()

        response = self.client.post(self.verify_url, {"token": "12ab"})

        self.assertContains(response, "6-digit code")
        self.assertNotLoggedIn()

    def test_correct_code_logs_in_with_verified_session(self):
        device = self.enable_2fa()
        self.post_password(next="/user/")

        code = current_code(device)
        response = self.client.post(self.verify_url, {"token": code[:3] + " " + code[3:]})

        self.assertRedirects(response, "/user/", fetch_redirect_response=False)
        self.assertLoggedIn()
        self.assertEqual(self.client.session[DEVICE_ID_SESSION_KEY], device.persistent_id)
        self.assertNotIn(auth_views.PENDING_2FA_USER_KEY, self.client.session)
        # two_factor_required views accept the OTP-verified session (no cookie needed).
        self.assertEqual(self.client.get("/user/").json(), {"id": self.user.pk})

    def test_code_cannot_be_reused(self):
        device = self.enable_2fa()
        code = current_code(device)
        self.post_password()
        self.client.post(self.verify_url, {"token": code})
        self.client.logout()

        self.post_password()
        response = self.client.post(self.verify_url, {"token": code})

        self.assertNotLoggedIn()
        self.assertContains(response, "already used. Wait for the next code in Authy")

    def test_repeated_failures_are_throttled(self):
        device = self.enable_2fa()
        self.post_password()
        self.client.post(self.verify_url, {"token": "000000"})

        # Even the right code is refused while the device is locked.
        response = self.client.post(self.verify_url, {"token": current_code(device)})

        self.assertContains(response, "Too many failed attempts")
        self.assertNotLoggedIn()

    def test_pending_login_expires(self):
        device = self.enable_2fa()
        self.post_password()
        session = self.client.session
        session[auth_views.PENDING_2FA_EXPIRES_KEY] = time.time() - 1
        session.save()

        response = self.client.post(self.verify_url, {"token": current_code(device)})

        self.assertRedirects(response, self.home_url, fetch_redirect_response=False)
        self.assertNotLoggedIn()
        self.assertContains(self.client.get(self.home_url), "expired")

    def test_code_page_without_password_step_redirects(self):
        response = self.client.get(self.verify_url)

        self.assertRedirects(response, self.home_url, fetch_redirect_response=False)

    def test_django_accounts_login_cannot_skip_2fa(self):
        self.enable_2fa()

        response = self.client.post(
            reverse("login"), {"username": "player", "password": PASSWORD}
        )

        self.assertRedirects(response, self.verify_url, fetch_redirect_response=False)
        self.assertNotLoggedIn()


class AuthenticatorAppChoiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("player", "player@example.com", PASSWORD)
        self.client.force_login(self.user, backend=MODEL_BACKEND)
        self.url = reverse("srcs_auth:totp-create")

    def test_default_app_is_google_authenticator(self):
        response = self.client.get(self.url)

        self.assertEqual(response.json()["app_name"], "Google Authenticator")
        self.assertEqual(TOTPDevice.objects.get(user=self.user).name, "Google Authenticator")

    def test_choosing_authy_keeps_the_same_secret(self):
        google = self.client.get(self.url, {"app": "google"}).json()
        authy = self.client.get(self.url, {"app": "authy"}).json()

        self.assertEqual(authy["app_name"], "Authy")
        self.assertEqual(authy["totp_code"], google["totp_code"])
        self.assertEqual(TOTPDevice.objects.get(user=self.user).name, "Authy")

    def test_qr_code_carries_the_issuer(self):
        self.client.get(self.url, {"app": "authy"})

        config_url = TOTPDevice.objects.get(user=self.user).config_url

        self.assertTrue(config_url.startswith("otpauth://totp/Transcendence%3Aplayer?"))
        self.assertIn("issuer=Transcendence", config_url)

    def test_unknown_app_is_rejected(self):
        response = self.client.get(self.url, {"app": "sms"})

        self.assertEqual(response.status_code, 400)
        self.assertFalse(TOTPDevice.objects.filter(user=self.user).exists())

    def test_service_rejects_unknown_app(self):
        with self.assertRaises(ValueError):
            TOTPService().create_totp_code(self.user, "sms")

    def test_is_reused_token(self):
        service = TOTPService()
        service.create_totp_code(self.user, "google")
        device = TOTPDevice.objects.get(user=self.user)
        code = current_code(device)

        self.assertFalse(service.is_reused_token(device, "not-a-number"))
        self.assertFalse(service.is_reused_token(device, code))
        self.assertTrue(device.verify_token(code))
        self.assertTrue(service.is_reused_token(device, code))


class SignUpTestCase(TestCase):
    def test_signup_returns_to_login_page_with_message(self):
        response = self.client.post(
            reverse("srcs_auth:signup"),
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("srcs_home:home"))
        self.assertContains(response, "Account created")
        self.assertContains(response, 'name="password"')
        self.assertTrue(User.objects.filter(username="newbie").exists())
