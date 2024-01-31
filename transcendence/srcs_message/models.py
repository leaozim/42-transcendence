from django.db import models
from srcs_user.models import User
from srcs_chat.models import Chat

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=500, db_column='content')
    timestamp = models.DateTimeField(auto_now_add=True)
    last_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_user')

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # Atualiza o último usuário antes de salvar a mensagem
        last_message = Message.objects.filter(chat=self.chat).order_by('-timestamp').first()
        if last_message:
            self.last_user = last_message.user
        super().save(*args, **kwargs)
    
    def to_dict(self):
        return {
            'user': self.user.username,
            'avatar': self.user.avatar,
            'content': self.content,
        }

    class Meta:
        db_table = 'message'
