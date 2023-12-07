from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    id42 = models.IntegerField(unique=True, null=True, blank=True, db_column='id_42')
    description = models.CharField(max_length=300, blank=True)
    token2F = models.CharField(max_length=255, blank=True, db_column='token_2f')
    is2fActive = models.BooleanField(default=False, db_column='is_2f_active')
    avatar = models.CharField(max_length=255, blank=True)
    expGame = models.FloatField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    
