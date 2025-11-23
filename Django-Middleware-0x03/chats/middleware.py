import time
from django.http import HttpResponse

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # { ip_address : [timestamps_of_posts] }
        self.message_history = {}

        # Settings
        self.TIME_WINDOW = 60     # 60 seconds = 1 minute
        self.LIMIT = 5            # 5 messages per minute

    def __call__(self, request):
        # Only track POST requests (messages being sent)
        if request.method == "POST":
            ip = request.META.get("REMOTE_ADDR")
            now = time.time()

            # Create entry for new IPs
            if ip not in self.message_history:
                self.message_history[ip] = []

            # Remove timestamps older than 1 minute
            self.message_history[ip] = [
                t for t in self.message_history[ip] if now - t < self.TIME_WINDOW
            ]

            # Check if limit exceeded
            if len(self.message_history[ip]) >= self.LIMIT:
                return HttpResponse(
                    "Message limit exceeded. Try again later.",
                    status=429
                )

            # Add new message timestamp
            self.message_history[ip].append(now)

        return self.get_response(request)