from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from srcs_message.models import Message
from srcs_message.services import get_user_receiving_last_message, BOT_ID


@receiver(post_save, sender=Message)
def notify_message_created(sender, instance, created, **kwargs):

    if created:
        receiving_user = get_user_receiving_last_message(instance.user.id)

        sender_user_data = {
            "id": instance.user.id,
            "username": instance.user.username,
            "avatar": instance.user.avatar,
        }

        json_sender_user_data = JsonResponse(sender_user_data).content.decode("utf-8")

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"chat_update.{receiving_user.id}",
            {
                "type": "chat_message_update",
                "data": json_sender_user_data,
            },
        )

        if (sender_user_data['id'] == BOT_ID):
            async_to_sync(channel_layer.group_send)(
            f"chat_{instance.chat.id}_{receiving_user.id}",
            {
                "type": "chat_message",
                "message": instance.content,
                "user_id": instance.user.id,
                "username": instance.user.username,
                "avatar": instance.user.avatar,
            },
        )
