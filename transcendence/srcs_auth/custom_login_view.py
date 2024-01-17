from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from srcs_user.models import User
# @login_required
class TOTPCreateView(LoginRequiredMixin, View):
    """
    Use this endpoint to set up a new TOTP device
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        device = self.get_user_totp_device(user)
        if not device:
            device = TOTPDevice.objects.create(user=user, confirmed=False)
        url = device.config_url
        return JsonResponse({'url': url}, status=201)

    def get_user_totp_device(self, user, confirmed=None):
        devices = TOTPDevice.objects.devices_for_user(user, confirmed=confirmed)
        for device in devices:
            if isinstance(device, TOTPDevice):
                return device

from django.utils.decorators import method_decorator
import logging
logger = logging.getLogger(__name__)

# @login_required
# @method_decorator(csrf_exempt, name='dispatch')
# class TOTPVerifyView(LoginRequiredMixin, View):
#     """
#     Use this endpoint to verify/enable a TOTP device
#     """
#     print( "sororro")

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
import logging

def totp_verify_view(request, token):
    logger.info(f"Received POST request for TOTP verification with token: {token}")
    print( "user = ")

    user = request.user

    print( "user = ", user)
    device = get_user_totp_device(user)
    
    if device is not None and device.verify_token(token):
        if not device.confirmed:
            device.confirmed = True
            device.save()
            logger.info(f"TOTP verification successful for user: {user}")
            
            user_data = User.objects.get(id42=user['id_42'])
            user_data.is2fActive = True
            user_data.save()

        return JsonResponse({'success': True}, status=200)

    return JsonResponse({'error': 'Invalid token'}, status=400)

def get_user_totp_device(user, confirmed=None):
    devices = TOTPDevice.objects.devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device