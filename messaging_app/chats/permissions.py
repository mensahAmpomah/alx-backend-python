from rest_framework import permissions
from .models import Conversation


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants to:
    - view (GET)
    - send (POST)
    - update (PUT/PATCH)
    - delete (DELETE)
    """

    SAFE_METHODS = ["GET"]

    def has_permission(self, request, view):
        # User must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        obj will be Message or Conversation.
        Check if the user is a participant before allowing any action.
        """

        # Determine conversation from Message or Conversation instance
        if hasattr(obj, "conversation"):
            conversation = obj.conversation
        elif isinstance(obj, Conversation):
            conversation = obj
        else:
            return False

        # Check if user is participant
        is_participant = conversation.participants.filter(id=request.user.id).exists()
        if not is_participant:
            return False

        # Allow participants to use all methods (GET, POST, PUT, PATCH, DELETE)
        if request.method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            return True

        return False