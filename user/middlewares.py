from datetime import datetime

from django.utils import timezone
from user.models import User


class UpdateLastActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = request.user
        if user.is_authenticated:
            user.last_activity = timezone.now()
            user.save()
        return response
