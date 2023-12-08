from django.db import models
from pong_users.models import User

class Chat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_chats')
    isPublic = models.BooleanField(default=False,db_column='is_public')
    password = models.BinaryField(null=True)
    muteds = models.ManyToManyField(User,related_name='muteds_chats',  blank=True)
    admins = models.ManyToManyField(User, related_name='admins_chats', blank=True)
    banneds = models.ManyToManyField(User, related_name='banned_chats', blank=True) 
    messages = models.ManyToManyField(
        User, 
        through="Message",
        through_fields=("chat", "user"))
    usersChats =  models.ManyToManyField(User, related_name='users_chats', blank=True) 
    

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, db_column='content')
    dateTime = models.DateTimeField(db_column='date_time')

    class Meta:
        db_table = 'message'


# class Match(models.Model):
#     leftPlayerId = models.IntegerField(unique=True, db_column='left_player_id')
#     leftPlayer = models.OneToOneField(User, related_name='left_player_match', on_delete=models.CASCADE, db_column='left_player')
#     rightPlayerId = models.IntegerField(unique=True, db_column='right_player_id')
#     rightPlayer = models.OneToOneField(User, related_name='right_player_match', on_delete=models.CASCADE, db_column='right_player')
#     leftPlayerScore = models.IntegerField(db_column='left_player_score')
#     rightPlayerScore = models.IntegerField(db_column='right_player_score')
#     date = models.DateTimeField()

#     class Meta:
#         db_table = 'match'