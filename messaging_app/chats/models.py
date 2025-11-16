import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# ENUM for user roles
USER_ROLES = [
    ("guest", "Guest"),
    ("host", "Host"),
    ("admin", "Admin"),
]

class User(AbstractUser):
    """Custom User model extending Django's AbstractUser"""
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default="guest")
    created_at = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]


class Conversation(models.Model):
    """Conversation between multiple users"""
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participants_emails = ", ".join([user.email for user in self.participants.all()])
        return f"Conversation {self.conversation_id} ({participants_emails})"


class Message(models.Model):
    """Messages sent by users in a conversation"""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.email}"
