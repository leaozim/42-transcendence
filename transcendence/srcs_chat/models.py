from django.db import models
from srcs_user.models import User

class Chat(models.Model):
    blocked = models.BooleanField(default=False) 
    users_on_chat = models.ManyToManyField(
        User, 
        related_name='users_chats', 
        blank=True, 
        db_column='users_chats') 
  
    class Meta:
        db_table = 'chat'

