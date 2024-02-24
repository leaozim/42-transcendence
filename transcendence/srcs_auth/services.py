import base64
import os
from io import BytesIO
from urllib.parse import parse_qs, urlparse

import qrcode
import requests
from django_otp.plugins.otp_totp.models import TOTPDevice


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
    def create_totp_code(self, user):
        device = self.get_user_totp_device(user)

        if not device:
            device = TOTPDevice.objects.create(user=user, confirmed=False)

        url = device.config_url
        totp_code = self.parse_totp_secret(url)
        qr_code = self.create_qrcode(url)
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
