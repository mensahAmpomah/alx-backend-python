from django.http import HttpResponseForbidden

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check authenticated users
        if request.user.is_authenticated:
            # Assuming user has a 'role' attribute
            role = getattr(request.user, "role", None)
            if role not in ["admin", "moderator"]:
                return HttpResponseForbidden("You do not have permission to perform this action.")
        else:
            # If user is not authenticated, also block
            return HttpResponseForbidden("You do not have permission to perform this action.")

        response = self.get_response(request)
        return response