from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with explicit CharFields"""
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    phone_number = serializers.CharField(allow_blank=True, allow_null=True)
    role = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "user_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "role",
            "created_at",
        ]
        read_only_fields = ["user_id", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model with nested sender and SerializerMethodField"""
    sender = UserSerializer(read_only=True)
    message_body = serializers.CharField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            "message_id",
            "sender",
            "message_body",
            "preview",
            "sent_at",
        ]
        read_only_fields = ["message_id", "sent_at"]

    def get_preview(self, obj):
        """Return first 20 characters of message as preview"""
        return obj.message_body[:20] if obj.message_body else ""


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation with nested participants and messages"""
    participants = UserSerializer(many=True)  # writable nested
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "messages",
            "message_count",
            "created_at",
        ]
        read_only_fields = ["conversation_id", "created_at"]

    def get_message_count(self, obj):
        """Return total number of messages in conversation"""
        return obj.messages.count()

    def validate_participants(self, value):
        """Ensure conversation has at least one participant"""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "Conversation must have at least one participant"
            )
        return value