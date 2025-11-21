from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # -------------------------------
    # 1. Filter messages by conversation_id
    # -------------------------------
    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")

        # If URL did not provide conversation_id
        if conversation_id is None:
            return Message.objects.none()

        return Message.objects.filter(conversation_id=conversation_id)

    # -------------------------------
    # 2. Validate POST: user must be a participant
    # -------------------------------
    def perform_create(self, serializer):
        user = self.request.user
        conversation = serializer.validated_data.get("conversation")

        # ensure participant
        if not conversation.participants.filter(id=user.id).exists():
            raise PermissionDenied("You are not allowed to post in this conversation.")

        serializer.save(sender=user)

    # -------------------------------
    # 3. Override destroy() to use HTTP_403_FORBIDDEN
    # -------------------------------
    def destroy(self, request, *args, **kwargs):
        message = self.get_object()

        # if user is NOT a participant (extra protection)
        if not message.conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are forbidden from deleting this message."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    # -------------------------------
    # 4. Override update() to handle PUT/PATCH with 403
    # -------------------------------
    def update(self, request, *args, **kwargs):
        message = self.get_object()

        if not message.conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are forbidden from editing this message."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)