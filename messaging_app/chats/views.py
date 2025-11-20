from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend  # <-- add this
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, and creating conversations.
    Also supports sending messages in a conversation.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated,]
    filter_backends = [DjangoFilterBackend]  # <-- enable filtering
    filterset_fields = ['participants__user_id']  # example: filter by participant

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        """
        Custom action to send a message in this conversation.
        POST /conversations/{id}/send_message/
        Expects JSON:
        {
            "sender": <user_id>,
            "message_body": "Hello"
        }
        """
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing, retrieving, and creating messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes=[IsAuthenticated,]
    filter_backends = [DjangoFilterBackend]  # <-- enable filtering
    filterset_fields = ['sender__user_id', 'conversation__conversation_id']  # example