import contextlib

from asgiref.sync import iscoroutinefunction, markcoroutinefunction


class AutoCreateAdminMiddleware:
    async_capable = True
    sync_capable = True

    def __init__(self, get_response):
        from django.contrib.auth.models import User

        # One-time configuration and initialization.
        self.get_response = get_response
        with contextlib.suppress(Exception):
            User.objects.create_superuser(
                username="admin", email="admin@example.com", password="password"
            )

        if iscoroutinefunction(self.get_response):
            markcoroutinefunction(self)

    def __call__(self, request):
        if iscoroutinefunction(self.get_response):

            async def async_call():
                return await self.get_response(request)

            return async_call()

        return self.get_response(request)
