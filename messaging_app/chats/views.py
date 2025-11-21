from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # add filtering
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    # add pagination + filtering
    pagination_class = MessagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")

        if conversation_id is None:
            return Message.objects.none()

        return Message.objects.filter(conversation_id=conversation_id).order_by("-timestamp")

    def perform_create(self, serializer):
        user = self.request.user
        conversation = serializer.validated_data.get("conversation")

        if not conversation.participants.filter(id=user.id).exists():
            raise PermissionDenied("You are not allowed to post in this conversation.")

        serializer.save(sender=user)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()

        if not message.conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are forbidden from deleting this message."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        message = self.get_object()

        if not message.conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You are forbidden from editing this message."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)