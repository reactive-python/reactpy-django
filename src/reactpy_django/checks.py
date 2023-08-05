import sys

from django.contrib.staticfiles.finders import find
from django.core.checks import Error, Tags, Warning, register


@register(Tags.compatibility)
def reactpy_warnings(app_configs, **kwargs):
    from django.conf import settings
    from django.urls import reverse

    from reactpy_django.config import REACTPY_FAILED_COMPONENTS

    warnings = []

    # REACTPY_DATABASE is not an in-memory database.
    if (
        getattr(settings, "DATABASES", {})
        .get(getattr(settings, "REACTPY_DATABASE", "default"), {})
        .get("NAME", None)
        == ":memory:"
    ):
        warnings.append(
            Warning(
                "Using ReactPy with an in-memory database can cause unexpected "
                "behaviors.",
                hint="Configure settings.py:DATABASES[REACTPY_DATABASE], to use a "
                "multiprocessing and thread safe database.",
                id="reactpy_django.W001",
            )
        )

    # ReactPy URLs exist
    try:
        reverse("reactpy:web_modules", kwargs={"file": "example"})
        reverse("reactpy:view_to_component", kwargs={"view_path": "example"})
    except Exception:
        warnings.append(
            Warning(
                "ReactPy URLs have not been registered.",
                hint="""Add 'path("reactpy/", include("reactpy_django.http.urls"))' """
                "to your application's urlpatterns.",
                id="reactpy_django.W002",
            )
        )

    # Warn if REACTPY_BACKHAUL_THREAD is set to True on Linux with Daphne
    if (
        sys.argv
        and sys.argv[0].endswith("daphne")
        and getattr(settings, "REACTPY_BACKHAUL_THREAD", True)
        and sys.platform == "linux"
    ):
        warnings.append(
            Warning(
                "REACTPY_BACKHAUL_THREAD is enabled but you running with Daphne on Linux. "
                "This configuration is known to be unstable.",
                hint="Set settings.py:REACTPY_BACKHAUL_THREAD to False or use a different webserver.",
                id="reactpy_django.W003",
            )
        )

    # Check if reactpy_django/client.js is available
    if not find("reactpy_django/client.js"):
        warnings.append(
            Warning(
                "ReactPy client.js could not be found within Django static files!",
                hint="Check your Django static file configuration.",
                id="reactpy_django.W004",
            )
        )

    # Check if any components failed to be registered
    if REACTPY_FAILED_COMPONENTS:
        warnings.append(
            Warning(
                "ReactPy failed to register the following components:\n\t+ "
                + "\n\t+ ".join(REACTPY_FAILED_COMPONENTS),
                hint="Check if these paths are valid, or if an exception is being raised during import.",
                id="reactpy_django.W005",
            )
        )

    return warnings


@register(Tags.compatibility)
def reactpy_errors(app_configs, **kwargs):
    from django.conf import settings

    errors = []

    # Make sure ASGI is enabled
    if not getattr(settings, "ASGI_APPLICATION", None):
        errors.append(
            Error(
                "ASGI_APPLICATION is not defined, but ReactPy requires ASGI.",
                hint="Add ASGI_APPLICATION to settings.py.",
                id="reactpy_django.E001",
            )
        )

    # DATABASE_ROUTERS is properly configured when REACTPY_DATABASE is defined
    if getattr(
        settings, "REACTPY_DATABASE", None
    ) and "reactpy_django.database.Router" not in getattr(
        settings, "DATABASE_ROUTERS", []
    ):
        errors.append(
            Error(
                "ReactPy database has been changed but the database router is "
                "not configured.",
                hint="Set settings.py:DATABASE_ROUTERS to "
                "['reactpy_django.database.Router', ...]",
                id="reactpy_django.E002",
            )
        )

    # All settings in reactpy_django.conf are the correct data type
    if not isinstance(getattr(settings, "REACTPY_WEBSOCKET_URL", ""), str):
        errors.append(
            Error(
                "Invalid type for REACTPY_WEBSOCKET_URL.",
                hint="REACTPY_WEBSOCKET_URL should be a string.",
                obj=settings.REACTPY_WEBSOCKET_URL,
                id="reactpy_django.E003",
            )
        )
    if not isinstance(getattr(settings, "REACTPY_RECONNECT_MAX", 0), int):
        errors.append(
            Error(
                "Invalid type for REACTPY_RECONNECT_MAX.",
                hint="REACTPY_RECONNECT_MAX should be an integer.",
                obj=settings.REACTPY_RECONNECT_MAX,
                id="reactpy_django.E004",
            )
        )
    if not isinstance(getattr(settings, "REACTPY_CACHE", ""), str):
        errors.append(
            Error(
                "Invalid type for REACTPY_CACHE.",
                hint="REACTPY_CACHE should be a string.",
                obj=settings.REACTPY_CACHE,
                id="reactpy_django.E005",
            )
        )
    if not isinstance(getattr(settings, "REACTPY_DATABASE", ""), str):
        errors.append(
            Error(
                "Invalid type for REACTPY_DATABASE.",
                hint="REACTPY_DATABASE should be a string.",
                obj=settings.REACTPY_DATABASE,
                id="reactpy_django.E006",
            )
        )
    if not isinstance(
        getattr(settings, "REACTPY_DEFAULT_QUERY_POSTPROCESSOR", ""), str
    ):
        errors.append(
            Error(
                "Invalid type for REACTPY_DEFAULT_QUERY_POSTPROCESSOR.",
                hint="REACTPY_DEFAULT_QUERY_POSTPROCESSOR should be a string.",
                obj=settings.REACTPY_DEFAULT_QUERY_POSTPROCESSOR,
                id="reactpy_django.E007",
            )
        )
    if not isinstance(getattr(settings, "REACTPY_AUTH_BACKEND", ""), str):
        errors.append(
            Error(
                "Invalid type for REACTPY_AUTH_BACKEND.",
                hint="REACTPY_AUTH_BACKEND should be a string.",
                obj=settings.REACTPY_AUTH_BACKEND,
                id="reactpy_django.E008",
            )
        )

    # Check for dependencies
    if "channels" not in settings.INSTALLED_APPS:
        errors.append(
            Error(
                "Django Channels is not installed.",
                hint="Add 'channels' to settings.py:INSTALLED_APPS.",
                id="reactpy_django.E009",
            )
        )

    return errors
