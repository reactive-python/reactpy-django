import contextlib

from asgiref.sync import iscoroutinefunction, markcoroutinefunction


class AutoCreateAdminMiddleware:
    async_capable = True
    sync_capable = False

    def __init__(self, get_response):
        from django.contrib.auth.models import User

        # One-time configuration and initialization.
        self.get_response = get_response
        with contextlib.suppress(Exception):
            User.objects.create_superuser(username="admin", email="admin@example.com", password="password")

        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    async def __call__(self, request):
        return await self.get_response(request)
