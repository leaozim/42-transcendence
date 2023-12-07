from django.db import models
from pong_users.models import User

class Chat(models.Model):
    ownerId = models.IntegerField(unique=True, db_column='owner_id')
    isPublic = models.IntegerField(db_column='is_public')
    password = models.BinaryField(null=True)
    banneds = models.ManyToManyField(User, related_name='chats_banned', blank=True)
    owner = models.OneToOneField(User, related_name='chats_owned', on_delete=models.CASCADE, db_column='owner')
#     messages = models.ManyToManyField('Message', related_name='chat_messages', blank=True)
#     muteds = models.ManyToManyField('MutedOnChat', related_name='chat_muted', blank=True)
#     usersChats = models.ManyToManyField('UsersOnChat', related_name='chat_users', blank=True)

#     class Meta:
#         db_table = 'chats'
        
# class UsersOnChat(models.Model):
#     chatId = models.IntegerField(db_column='chat_id')
#     userId = models.IntegerField(db_column='user_id')
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, db_column='chat')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user')

#     class Meta:
#         unique_together = ('chatId', 'userId')
#         db_table = 'users_on_chat'

# class AdminOnChat(models.Model):
#     chatId = models.IntegerField(db_column='chat_id')
#     adminId = models.IntegerField(db_column='admin_id')
#     admin = models.ForeignKey(User, on_delete=models.CASCADE, db_column='admin')
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, db_column='chat')

#     class Meta:
#         unique_together = ('chatId', 'adminId')
#         db_table = 'admin_on_chat'

# class MutedOnChat(models.Model):
#     chatId = models.IntegerField(db_column='chat_id')
#     mutedId = models.IntegerField(db_column='muted_id')
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, db_column='chat')
#     muted = models.ForeignKey(User, on_delete=models.CASCADE, db_column='muted')

#     class Meta:
#         unique_together = ('chatId', 'mutedId')
#         db_table = 'muted_on_chat'

# class Message(models.Model):
#     idAuthor = models.IntegerField(db_column='id_author')
#     content = models.CharField(max_length=500, db_column='content')
#     dateTime = models.DateTimeField(db_column='date_time')
#     chatId = models.IntegerField(db_column='chat_id')
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, db_column='chat')

#     class Meta:
#         db_table = 'message'

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