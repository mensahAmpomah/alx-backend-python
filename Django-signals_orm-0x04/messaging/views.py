from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Message


@login_required
def inbox(request):
    user = request.user

    messages = (
        Message.objects
        .filter(receiver=user, parent_message__isnull=True)
        .select_related("sender", "receiver", "edited_by")
        .prefetch_related("replies__sender", "replies__edited_by")
        .order_by("-timestamp")
    )

    return render(request, "messaging/inbox.html", {"messages": messages})
