import base64
import os
import time
from io import BytesIO
from urllib.parse import parse_qs, urlparse

import qrcode
import requests
from django.utils.translation import gettext_lazy as _
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice

# Authenticator apps offered when enabling two-factor authentication.
# Both implement standard TOTP (RFC 6238), so the same QR code / setup key works
# in either; the choice selects the setup instructions and is remembered (as the
# device name) to tell the user which app to open when logging in.
AUTHENTICATOR_APPS = {
    "google": {
        "name": "Google Authenticator",
        "instructions": _(
            'Open Google Authenticator, tap "+" and choose "Scan a QR code". '
            'Or choose "Enter a setup key" and type the key below.'
        ),
        "android": "https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2",
        "ios": "https://apps.apple.com/app/google-authenticator/id388497605",
    },
    "authy": {
        "name": "Authy",
        "instructions": _(
            'Open Authy, tap "+" (Add account) and choose "Scan QR code". '
            'Or choose "Enter key manually" and type the key below.'
        ),
        "android": "https://play.google.com/store/apps/details?id=com.authy.authy",
        "ios": "https://apps.apple.com/app/twilio-authy/id494168017",
    },
}
DEFAULT_AUTHENTICATOR_APP = "google"


def get_access_token(code: str):
    data = {
        "client_id": os.environ.get("CLIENT_ID"),
        "client_secret": os.environ.get("CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ.get("REDIRECT_URI"),
        "scope": "identify",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        "https://api.intra.42.fr/oauth/token", data=data, headers=headers
    )
    if not response.ok:
        raise ValueError(f"Fail to get token, check data:\nData = {data}")
    credentials = response.json()
    return credentials.get("access_token")


def get_user_info(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.intra.42.fr/v2/me", headers=headers)
    if not response.ok:
        raise Exception(
            "Fail to get user information, "
            f"check token and headers:\nHeaders = {headers}\nToken = {access_token}"
        )
    return response.json()


def exchange_code(code: str):
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    return user_info


class TOTPService:
    def create_totp_code(self, user, app=DEFAULT_AUTHENTICATOR_APP):
        if app not in AUTHENTICATOR_APPS:
            raise ValueError(f"Unknown authenticator app: {app}")
        app_name = AUTHENTICATOR_APPS[app]["name"]
        device = self.get_user_totp_device(user)

        if not device:
            device = TOTPDevice.objects.create(user=user, name=app_name, confirmed=False)
        elif device.name != app_name:
            device.name = app_name
            device.save(update_fields=["name"])

        url = device.config_url
        totp_code = self.parse_totp_secret(url)
        qr_code = self.create_qrcode(url)
        user.is_2f_active = True
        return qr_code, totp_code

    def verify_totp_token(self, user, token) -> bool:
        device = self.get_user_totp_device(user)

        if device is not None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
                user.is_2f_active = True
                user.save()
            return True

        return False

    def is_reused_token(self, device, token) -> bool:
        """True if ``token`` is correct for the current time but was already used.

        django_otp refuses to accept the same code twice (replay protection), which
        users hit when they log in right after enabling two-factor authentication.
        """
        try:
            token = int(token)
        except (TypeError, ValueError):
            return False
        totp = TOTP(device.bin_key, device.step, device.t0, device.digits, device.drift)
        totp.time = time.time()
        return totp.verify(token, device.tolerance) and totp.t() <= device.last_t

    def delete_totp_devices(self, user):
        devices = self.get_user_totp_devices(user)

        if not devices:
            return False

        for device in devices:
            device.delete()

        user.is_2f_active = False
        user.save()
        return True

    def get_user_totp_device(self, user, confirmed=None):
        devices = self.get_user_totp_devices(user, confirmed=confirmed)
        for device in devices:
            if isinstance(device, TOTPDevice):
                return device

    def parse_totp_secret(self, config_url):
        parsed_url = urlparse(config_url)
        query_params = parse_qs(parsed_url.query)
        secret_values = query_params.get("secret", [])
        return secret_values[0] if secret_values else None

    def create_qrcode(self, config_url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(config_url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_img.save(buffer)
        qr_bytes = buffer.getvalue()
        return base64.b64encode(qr_bytes).decode("utf-8")

    def get_user_totp_devices(self, user, confirmed=None):
        devices = TOTPDevice.objects.devices_for_user(user, confirmed=confirmed)
        return devices


