from django.db import models
from srcs_users.models import User

class Chat(models.Model):
    blocked = models.BooleanField(default=False) 
    messages = models.ManyToManyField(
        User, 
        through="Message",
        through_fields=("chat", "user"), blank=True)
    usersChats =  models.ManyToManyField(User, related_name='users_chats', blank=True, db_column='users_chats') 
    


