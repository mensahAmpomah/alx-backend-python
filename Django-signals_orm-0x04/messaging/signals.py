from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
from django.contrib.auth.models import User

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



@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    This signal runs BEFORE a Message is updated.
    It checks if the 'content' is being changed.
    If yes, it saves the old content into MessageHistory.
    """

    if instance.pk:  # message already exists (not new)
        old_message = Message.objects.get(pk=instance.pk)

        # Only log if content was actually changed
        if old_message.content != instance.content:

            # Save history
            MessageHistory.objects.create(
                message=instance,
                old_content=old_message.content
            )

            # Mark message as edited
            instance.edited = True


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    Removes all remaining objects related to the deleted user.
    """

    # Delete notifications sent to the user
    Notification.objects.filter(user=instance).delete()

    # Delete history records where the user was the editor
    MessageHistory.objects.filter(edited_by=instance).delete()

    # Extra safety cleanup (in case cascade didn't catch everything):
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()