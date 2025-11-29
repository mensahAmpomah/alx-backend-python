from django.db import models
from django.contrib.auth.models import User


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to get unread messages for a user.
    """

    def for_user(self, user):
        return self.filter(receiver=user, read=False).only(
            "id", "sender", "content", "timestamp", "parent_message"
        )

class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="edited_messages"
    )

    # NEW: For threaded replies
    parent_message = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    def __str__(self):
        if self.parent_message:
            return f"Reply by {self.sender} to Message {self.parent_message.id}"
        return f"Message from {self.sender} to {self.receiver}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="notifications"
    )
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"




class MessageHistory(models.Model):
    """
    Stores old content of messages BEFORE they are edited.
    """
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="history"
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for Message {self.message.id}"