from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Message


@login_required
def inbox(request):
    """
    Shows all top-level messages (not replies),
    optimized using select_related and prefetch_related.
    """

    messages = (
        Message.objects
        .filter(receiver=request.user, parent_message__isnull=True)  # <-- FILTER
        .select_related("sender", "receiver", "edited_by")            # <-- select_related
        .prefetch_related("replies")                                  # <-- prefetch replies
        .order_by("-timestamp")
    )

    return render(request, "messaging/inbox.html", {"messages": messages})