from django.db import models
from srcs_users.models import User
# from srcs_message.models import Message


class Chat(models.Model):
    blocked = models.BooleanField(default=False) 
    messages = models.ManyToManyField(
        User, 
        through="Message",
        through_fields=("chat", "user"), blank=True)
    usersChats =  models.ManyToManyField(User, related_name='users_chats', blank=True, db_column='users_chats') 
  
    class Meta:
        db_table = 'chat'
  
# class Message(models.Model):
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.CharField(max_length=500, db_column='content')

#     class Meta:
#         db_table = 'message'

