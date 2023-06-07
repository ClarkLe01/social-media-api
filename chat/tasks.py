import channels.layers
from asgiref.sync import async_to_sync
from celery import shared_task


@shared_task
def send_notify(userId, data):
    channel_layer = channels.layers.get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{userId}",
        {
            "type": "message",
            "data": data
        },
    )
