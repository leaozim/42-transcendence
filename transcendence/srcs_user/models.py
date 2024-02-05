from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from srcs_user.managers import IntraUserOAuth2Manager

class User(AbstractUser, PermissionsMixin):
    objects = IntraUserOAuth2Manager()
    id_42 = models.IntegerField(unique=True, null=True, blank=True, db_column='id_42')
    description = models.TextField(blank=True)
    token_2F = models.CharField(max_length=255, blank=True, db_column='token_2f')
    is_2f_active = models.BooleanField(default=False, db_column='is_2f_active')
    avatar = models.CharField(max_length=255, blank=True, default='https://res.cloudinary.com/dw9xon1xs/image/upload/v1699535128/nico_nk9vdi.jpg')
    mmr = models.FloatField(default=0)
    
    @property
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    class Meta:
        db_table = 'user'