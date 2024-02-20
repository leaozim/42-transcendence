import factory
from django_otp.plugins.otp_totp.models import TOTPDevice
from srcs_user.models import User
from srcs_user.tests.factories import UserFactory
 
class TOTPDeviceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TOTPDevice

    user =  factory.SubFactory(UserFactory)
    confirmed = False
   
