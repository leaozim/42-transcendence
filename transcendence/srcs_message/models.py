from django.db import models
from srcs_chat.models import Chat
from srcs_user.models import User


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, db_column="content")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def to_dict(self):
        return {
            "user": self.user.username,
            "avatar": self.user.avatar,
            "content": self.content,
        }

    class Meta:
        db_table = "message"
