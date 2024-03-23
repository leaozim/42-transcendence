from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from srcs_message.models import Message
from srcs_message.services import get_user_receiving_last_message


@receiver(post_save, sender=Message)
def notify_message_created(sender, instance, created, **kwargs):
    import logging

    logging.getLogger("django.server").info("Test")
    if created:
        receiving_user = get_user_receiving_last_message(instance.user.id)

        receiving_user_data = {
            "id": receiving_user.id,
            "username": receiving_user.username,
            "avatar": receiving_user.avatar,
        }

        sender_user_data = {
            "id": instance.user.id,
            "username": instance.user.username,
            "avatar": instance.user.avatar,
        }

        json_receiving_user_data = JsonResponse(receiving_user_data).content.decode(
            "utf-8"
        )
        json_sender_user_data = JsonResponse(sender_user_data).content.decode("utf-8")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "chat_update",
        {
            "type": "chat_message_update",
            "user": instance.user.id,
            "data_receiving_user": json_receiving_user_data,
            "data_sender_user": json_sender_user_data,
        },
    )
