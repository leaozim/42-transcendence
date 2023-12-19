from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import IntraUserOAuth2Manager

class User(AbstractUser, PermissionsMixin):
    objects = IntraUserOAuth2Manager()
    id42 = models.IntegerField(unique=True, null=True, blank=True, db_column='id_42')
    description = models.TextField(blank=True)
    token2F = models.CharField(max_length=255, blank=True, db_column='token_2f')
    is2fActive = models.BooleanField(default=False, db_column='is_2f_active')
    avatar = models.CharField(max_length=255, blank=True)
    expGame = models.FloatField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    blockedUsers = models.ManyToManyField('self', symmetrical=False, related_name='blocking_users', blank=True, db_column='blocked_users')
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following_users', blank=True)
    friendships = models.ManyToManyField('self', symmetrical=False, related_name='friend_users', blank=True)
    
    @property
    def is_authenticated(self):
        return True