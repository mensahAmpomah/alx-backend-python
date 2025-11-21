from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def perform_create(self, serializer):
        """
        Automatically set the sender to the logged-in user.
        And make sure the sender is a participant.
        """
        user = self.request.user
        conversation = serializer.validated_data["conversation"]

        # Prevent sending messages to conversations you do not belong to
        if not conversation.participants.filter(id=user.id).exists():
            raise PermissionDenied("You are not a participant in this conversation")

        serializer.save(sender=user)