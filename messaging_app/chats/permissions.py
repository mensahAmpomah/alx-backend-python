from rest_framework import permissions
from .models import Conversation

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission:
    - Allow access only to authenticated users
    - Allow access only if the user is part of the conversation
    """

    def has_permission(self, request, view):
        # User must be logged in
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """
        obj will be a Message instance or Conversation instance.
        We check if the requesting user is inside obj.conversation.participants
        """
        conversation = None

        # If obj is a Message
        if hasattr(obj, "conversation"):
            conversation = obj.conversation

        # If obj is a Conversation
        elif isinstance(obj, Conversation):
            conversation = obj

        # If no conversation found, deny
        if conversation is None:
            return False

        # Check if the user is a participant
        return conversation.participants.filter(id=request.user.id).exists()