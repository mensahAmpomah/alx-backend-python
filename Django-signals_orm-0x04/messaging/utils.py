def get_thread(message):


    thread = {
        "message": message,
        "replies": []
    }

    for reply in message.replies.all():
        thread["replies"].append(get_thread(reply))

    return thread