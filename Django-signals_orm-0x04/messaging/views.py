from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from .models import Message
from django.contrib.auth.models import User 

@login_required
def send_message(request, receiver_id, parent_id=None):
    """
    Allows a user to send a new message OR reply to an existing one.
    `sender=request.user` is explicitly included.
    """

    receiver = get_object_or_404(User, id=receiver_id)
    parent_message = None

    if parent_id:
        parent_message = get_object_or_404(Message, id=parent_id)

    if request.method == "POST":
        content = request.POST.get("content")

        Message.objects.create(
            sender=request.user,             # REQUIRED — now included!
            receiver=receiver,
            content=content,
            parent_message=parent_message    # supports threaded replies
        )

        return redirect("inbox")

    return render(request, "messaging/send_message.html", {
        "receiver": receiver,
        "parent_message": parent_message
    })