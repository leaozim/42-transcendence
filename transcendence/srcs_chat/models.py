from django.db import models
from srcs_user.models import User

class Chat(models.Model):
    blocked = models.BooleanField(default=False) 
    users_on_chat = models.ManyToManyField(
        User, 
        related_name='users_chats', 
        blank=True, 
        db_column='users_chats')
    blocked_by = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
  
    class Meta:
        db_table = 'chat'

