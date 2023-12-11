from django.db import models
from pong_users.models import User

class Chat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_chats')
    isPublic = models.BooleanField(default=False, db_column='is_public')
    password = models.BinaryField(null=True)
    muteds = models.ManyToManyField(User,related_name='muteds_chats',  blank=True)
    admins = models.ManyToManyField(User, related_name='admins_chats', blank=True)
    banneds = models.ManyToManyField(User, related_name='banned_chats', blank=True) 
    messages = models.ManyToManyField(
        User, 
        through="Message",
        through_fields=("chat", "user"), blank=True)
    usersChats =  models.ManyToManyField(User, related_name='users_chats', blank=True, db_column='users_chats') 
    

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, db_column='content')
    dateTime = models.DateTimeField(db_column='date_time')

    class Meta:
        db_table = 'message'
