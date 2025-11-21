import django_filters
from .models import Message, Conversation
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageFilter(django_filters.FilterSet):
    # Messages sent after a certain date
    sent_after = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="gte"
    )

    # Messages sent before a certain date
    sent_before = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="lte"
    )

    # Filter messages by sender_id
    sender = django_filters.NumberFilter(field_name="sender__id", lookup_expr="exact")

    class Meta:
        model = Message
        fields = ["sender", "sent_after", "sent_before"]


class ConversationFilter(django_filters.FilterSet):
    # Find conversations with a specific user
    participant = django_filters.NumberFilter(
        field_name="participants__id", lookup_expr="exact"
    )

    class Meta:
        model = Conversation
        fields = ["participant"]