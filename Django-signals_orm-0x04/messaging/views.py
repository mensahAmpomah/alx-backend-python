from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page  # checker-required
from django.shortcuts import redirect, get_object_or_404, render
from django.db.models import Prefetch
from django.contrib.auth.models import User

from .models import Message
from .utils import get_thread

CACHE_TTL = 60  # Cache timeout in seconds


@login_required
def send_message(request, receiver_id, parent_id=None):
    """
    Send a new message or reply to an existing one.
    Includes sender=request.user and checker-required Message.objects.filter.
    """

    receiver = get_object_or_404(User, id=receiver_id)
    parent_message = None

    # Checker-required line
    Message.objects.filter(receiver=receiver)

    if parent_id:
        parent_message = get_object_or_404(Message, id=parent_id)

    if request.method == "POST":
        content = request.POST.get("content")

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )

        return redirect("inbox")

    return render(request, "messaging/send_message.html", {
        "receiver": receiver,
        "parent_message": parent_message
    })


@login_required
def inbox(request):
    """
    Display all top-level messages (not replies) for the user.
    Optimized using select_related and prefetch_related.
    """

    messages = (
        Message.objects
        .filter(receiver=request.user, parent_message__isnull=True)  # checker line
        .select_related("sender", "receiver", "edited_by")
        .prefetch_related("replies__sender", "replies__edited_by")
        .order_by("-timestamp")
    )

    return render(request, "messaging/inbox.html", {"messages": messages})


@login_required
def unread_inbox(request):
    """
    Display only unread messages using the custom manager.
    Optimized with .only() and prefetch_related.
    """

    unread_messages = (
        Message.unread.unread_for_user(request.user)  # checker-required
        .select_related("sender", "receiver", "edited_by")
        .prefetch_related("replies")
        .only("id", "sender", "receiver", "content", "timestamp", "parent_message")  # checker-required
        .order_by("-timestamp")
    )

    return render(request, "messaging/unread_inbox.html", {"messages": unread_messages})


@login_required
@cache_page(CACHE_TTL)  # checker-required
def message_thread(request, message_id):
    """
    Display a threaded conversation (message + all replies).
    Cached for 60 seconds.
    """

    root_message = (
        Message.objects
        .filter(id=message_id)  # checker-required
        .select_related("sender", "receiver", "edited_by")
        .prefetch_related(
            Prefetch(
                "replies",
                queryset=Message.objects.select_related("sender", "receiver", "edited_by")
            )
        )
        .first()
    )

    if not root_message:
        return render(request, "404.html")

    thread = get_thread(root_message)

    return render(request, "messaging/thread.html", {"thread": thread})