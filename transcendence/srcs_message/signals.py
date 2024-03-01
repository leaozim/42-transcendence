from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from srcs_message.models import Message
from srcs_chat.services import get_updated_user_list
from srcs_message.services import get_user_receiving_last_message
from django.core.serializers import serialize
from django.http import JsonResponse

@receiver(post_save, sender=Message)
def notification_created(sender, instance, created, **kwargs):
    if created:
        receiving = get_user_receiving_last_message(instance.user.id)
        receiving_data = {
            'id': receiving.id,
            'username': receiving.username,
            'avatar': receiving.avatar,
        }
        data_user = {
            'id': instance.user.id,
            'username': instance.user.username,
            'avatar': instance.user.avatar,
        }
        json_data = JsonResponse(receiving_data).content.decode('utf-8')
        json_data2 = JsonResponse(data_user).content.decode('utf-8')

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'chat_update',
            {
                "type": "chat_message_update",
                "user": instance.user.id,
                "data_receiving_user": json_data,
                "data_user": json_data2
            }
        )