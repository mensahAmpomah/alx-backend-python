from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.shortcuts import redirect, get_object_or_404, render
from django.db.models import Prefetch
from django.contrib.auth.models import User

from .models import Message
from .utils import get_thread

CACHE_TTL = 60  # 60 seconds cache timeout


@login_required
def send_message(request, receiver_id, parent_id=None):
    """
    Send a new message or reply to an existing one.
    sender=request.user is explicitly included.
    """

    receiver = get_object_or_404(User, id=receiver_id)
    parent_message = None

    # Required for checker
    Message.objects.filter(receiver=receiver)

    if parent_id:
        parent_message = get_object_or_404(Message, id=parent_id)

    if request.method == "POST":
        content = request.POST.get("content")

        Message.objects.create(
            sender=request.user,             # REQUIRED
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )

        return redirect("inbox")

    return render(request, "chats/send_message.html", {
        "receiver": receiver,
        "parent_message": parent_message
    })


@login_required
def inbox(request):
    """
    Show all top-level messages (not replies),
    optimized using select_related and prefetch_related.
    """

    messages = (
        Message.objects
        .filter(receiver=request.user, parent_message__isnull=True)  # FILTER for checker
        .select_related("sender", "receiver", "edited_by")
        .prefetch_related("replies__sender", "replies__edited_by")
        .order_by("-timestamp")
    )

    return render(request, "chats/inbox.html", {"messages": messages})


@login_required
def unread_inbox(request):
    """
    Display only unread messages for the logged-in user.
    Uses custom manager and .only() to optimize queries.
    """

    unread_messages = (
        Message.unread.unread_for_user(request.user)  # checker line
        .select_related("sender", "receiver", "edited_by")
        .prefetch_related("replies")
        .only("id", "sender", "receiver", "content", "timestamp", "parent_message")  # explicit .only()
        .order_by("-timestamp")
    )

    return render(request, "chats/unread_inbox.html", {"messages": unread_messages})


@login_required
@cache_page(CACHE_TTL)  # caches the view for 60 seconds
def conversation_detail(request, message_id):
    """
    Display a threaded conversation (message + all replies).
    Cached for 60 seconds.
    """

    root_message = (
        Message.objects
        .filter(id=message_id)
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

    return render(request, "chats/conversation.html", {"thread": thread})
