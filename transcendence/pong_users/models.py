from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id_42 = models.IntegerField(unique=True, null=True, blank=True)
    description = models.CharField(max_length=300, blank=True)
    token_2f = models.CharField(max_length=255, blank=True)
    is_2f_active = models.BooleanField(default=False, db_column='is_2f_active')
    avatar = models.CharField(max_length=255, blank=True)
    exp_game = models.FloatField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)