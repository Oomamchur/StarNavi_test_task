from django.utils import timezone
from rest_framework.response import Response


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request) -> Response:
        response = self.get_response(request)

        user = request.user
        if user.is_authenticated:
            user.last_activity = timezone.now()
            user.save()
        return response
