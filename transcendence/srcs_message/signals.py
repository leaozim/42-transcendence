from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from srcs_message.models import Message
from srcs_chat.services import get_updated_user_list

@receiver(post_save, sender=Message)
def notification_created(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        user_list = get_updated_user_list(instance.user.id, instance.user.username)

        async_to_sync(channel_layer.group_send)(
            'chat_update',
            {
                "type": "chat_message_update",
                "user": instance.user.id,
                "user_list": user_list

            }
        )