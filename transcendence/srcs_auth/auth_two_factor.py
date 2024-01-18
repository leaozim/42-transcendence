import qrcode
import base64

from io import BytesIO
from django.http import JsonResponse
from django.views import View
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from urllib.parse import parse_qs
from srcs_user.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from urllib.parse import parse_qs, urlparse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest

class TOTPCreateView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, *args, **kwargs):
        print(request)
        user = request.user
        device = self.get_user_totp_device(user)

        if not device:
            device = TOTPDevice.objects.create(user=user, confirmed=False)

        url = device.config_url
        totp_code = self.parse_totp_secret(url)
        qr_code = self.create_qrcode(url)
        user.is_2f_active = True
        user.save()
        return render(request, 'registration/totp_create.html', {'qrcode': qr_code, 'totp_code': totp_code})

    def get_user_totp_device(self, user, confirmed=None):
        devices = TOTPDevice.objects.devices_for_user(user, confirmed=confirmed)
        for device in devices:
            if isinstance(device, TOTPDevice):
                return device

    def parse_totp_secret(self, config_url):
        parsed_url = urlparse(config_url)
        query_params = parse_qs(parsed_url.query)
        secret_values = query_params.get('secret', [])
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
        return base64.b64encode(qr_bytes).decode('utf-8')

@method_decorator(csrf_exempt, name='dispatch')
class TOTPVerifyView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, token):
        user = request.user
        device = self.get_user_totp_device(user)

        if device is not None and device.verify_token(token):
            if not device.confirmed:
                device.confirmed = True
                device.save()
            return JsonResponse({'success': True}, status=200)
        
        return JsonResponse({'error': 'Invalid token'}, status=400)

    def get_user_totp_device(self, user, confirmed=None):
        devices = TOTPDevice.objects.devices_for_user(user, confirmed=confirmed)
        
        for device in devices:
            if isinstance(device, TOTPDevice):
                return device
            
        
class TOTPDeleteView(LoginRequiredMixin, View):
    def get_user_totp_devices(self, user):
        return TOTPDevice.objects.devices_for_user(user)

    def get(self, request: HttpRequest, *args, **kwargs):
            user = request.user
            devices = self.get_user_totp_devices(user)

            if not devices:
                return JsonResponse({'error': 'No TOTP devices found for the user'}, status=404)

            for device in devices:
                device.delete()
                
            user.is_2f_active = False
            user.save()
            return JsonResponse({'success': 'TOTP devices deleted successfully'}, status=200)