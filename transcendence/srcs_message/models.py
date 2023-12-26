from django.db import models
from srcs_user.models import User
from srcs_chat.models import Chat

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, db_column='content')

    class Meta:
        db_table = 'message'
