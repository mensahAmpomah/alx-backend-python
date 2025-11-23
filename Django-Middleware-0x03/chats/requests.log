from datetime import datetime

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.log_file = "requests.log"

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        path = request.path
        timestamp = datetime.now()

        log_message = f"{timestamp} - User: {user} - Path: {path}\n"

        with open(self.log_file, "a") as f:
            f.write(log_message)

        response = self.get_response(request)
        return response