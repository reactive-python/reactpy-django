from django.core.checks import Error, Tags, Warning, register


@register(Tags.compatibility)
def reactpy_warnings(app_configs, **kwargs):
    from django.conf import settings
    from django.urls import reverse

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

    # REACTPY_CACHE is not an in-memory cache.
    if getattr(settings, "CACHES", {}).get(
        getattr(settings, "REACTPY_CACHE", "default"), {}
    ).get("BACKEND", None) in {
        "django.core.cache.backends.dummy.DummyCache",
        "django.core.cache.backends.locmem.LocMemCache",
    }:
        warnings.append(
            Warning(
                "Using ReactPy with an in-memory cache can cause unexpected "
                "behaviors.",
                hint="Configure settings.py:CACHES[REACTPY_CACHE], to use a "
                "multiprocessing and thread safe cache.",
                id="reactpy_django.W002",
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
                id="reactpy_django.W003",
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
                "ASGI_APPLICATION is not defined."
                " ReactPy requires ASGI to be enabled.",
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

    return errors
