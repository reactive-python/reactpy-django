from reactpy_router.core import create_router

from reactpy_django.router.resolvers import DjangoResolver

django_router = create_router(DjangoResolver)
