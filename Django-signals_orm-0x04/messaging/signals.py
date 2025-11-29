from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_notification_for_message(sender, instance, created, **kwargs):
    """
    This signal runs automatically whenever a new Message is created.
    It creates a Notification for the receiver of the message.
    """

    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            text=f"You received a new message from {instance.sender.username}"
        )