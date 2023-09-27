import contextlib
import math
import sys

from django.contrib.staticfiles.finders import find
from django.core.checks import Error, Tags, Warning, register
from django.template import loader
from django.urls import NoReverseMatch


@register(Tags.compatibility)
def reactpy_warnings(app_configs, **kwargs):
    from django.conf import settings
    from django.urls import reverse

    from reactpy_django import config
    from reactpy_django.config import REACTPY_FAILED_COMPONENTS

    warnings = []
    INSTALLED_APPS: list[str] = getattr(settings, "INSTALLED_APPS", [])

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
        reverse("reactpy:view_to_iframe", kwargs={"dotted_path": "example"})
    except Exception:
        warnings.append(
            Warning(
                "ReactPy URLs have not been registered.",
                hint="""Add 'path("reactpy/", include("reactpy_django.http.urls"))' """
                "to your application's urlpatterns. If this application does not need "
                "to render ReactPy components, you add this warning to SILENCED_SYSTEM_CHECKS.",
                id="reactpy_django.W002",
            )
        )

    # Warn if REACTPY_BACKHAUL_THREAD is set to True with Daphne
    if (
        sys.argv[0].endswith("daphne")
        or ("runserver" in sys.argv and "daphne" in INSTALLED_APPS)
    ) and getattr(settings, "REACTPY_BACKHAUL_THREAD", False):
        warnings.append(
            Warning(
                "Unstable configuration detected. REACTPY_BACKHAUL_THREAD is enabled "
                "and you running with Daphne.",
                hint="Set settings.py:REACTPY_BACKHAUL_THREAD to False or use a different web server.",
                id="reactpy_django.W003",
            )
        )

    # Check if reactpy_django/client.js is available
    if not find("reactpy_django/client.js"):
        warnings.append(
            Warning(
                "ReactPy client.js could not be found within Django static files!",
                hint="Check all static files related Django settings and INSTALLED_APPS.",
                id="reactpy_django.W004",
            )
        )

    # Check if any components failed to be registered
    if REACTPY_FAILED_COMPONENTS:
        warnings.append(
            Warning(
                "ReactPy failed to register the following components:\n\t+ "
                + "\n\t+ ".join(REACTPY_FAILED_COMPONENTS),
                hint="Check if these paths are valid, or if an exception is being "
                "raised during import.",
                id="reactpy_django.W005",
            )
        )

    # Check if the reactpy/component.html template exists
    try:
        loader.get_template("reactpy/component.html")
    except Exception:
        warnings.append(
            Warning(
                "ReactPy HTML templates could not be found!",
                hint="Check your settings.py:TEMPLATES configuration and make sure "
                "ReactPy-Django is installed properly.",
                id="reactpy_django.W006",
            )
        )

    # DELETED W007: Check if REACTPY_WEBSOCKET_URL doesn't end with a slash
    # DELETED W008: Check if REACTPY_WEBSOCKET_URL doesn't start with an alphanumeric character

    # Removed REACTPY_WEBSOCKET_URL setting
    if getattr(settings, "REACTPY_WEBSOCKET_URL", None):
        warnings.append(
            Warning(
                "REACTPY_WEBSOCKET_URL has been removed.",
                hint="Use REACTPY_URL_PREFIX instead.",
                id="reactpy_django.W009",
            )
        )

    # Check if REACTPY_URL_PREFIX is being used properly in our HTTP URLs
    with contextlib.suppress(NoReverseMatch):
        full_path = reverse("reactpy:web_modules", kwargs={"file": "example"}).strip(
            "/"
        )
        reactpy_http_prefix = f'{full_path[: full_path.find("web_module/")].strip("/")}'
        if reactpy_http_prefix != config.REACTPY_URL_PREFIX:
            warnings.append(
                Warning(
                    "HTTP paths are not prefixed with REACTPY_URL_PREFIX. "
                    "Some ReactPy features may not work as expected.",
                    hint="Use one of the following solutions.\n"
                    "\t1) Utilize REACTPY_URL_PREFIX within your urls.py:\n"
                    f'\t     path("{config.REACTPY_URL_PREFIX}/", include("reactpy_django.http.urls"))\n'
                    "\t2) Modify settings.py:REACTPY_URL_PREFIX to match your existing HTTP path:\n"
                    f'\t     REACTPY_URL_PREFIX = "{reactpy_http_prefix}/"\n'
                    "\t3) If you not rendering components by this ASGI application, then remove "
                    "ReactPy HTTP and websocket routing. This is common for configurations that "
                    "rely entirely on `host` configuration in your template tag.",
                    id="reactpy_django.W010",
                )
            )

    # Check if REACTPY_URL_PREFIX is empty
    if not getattr(settings, "REACTPY_URL_PREFIX", "reactpy/"):
        warnings.append(
            Warning(
                "REACTPY_URL_PREFIX should not be empty!",
                hint="Change your REACTPY_URL_PREFIX to be written in the following format: '/example_url/'",
                id="reactpy_django.W011",
            )
        )

    # Check if `daphne` is not in installed apps when using `runserver`
    if "runserver" in sys.argv and "daphne" not in getattr(
        settings, "INSTALLED_APPS", []
    ):
        warnings.append(
            Warning(
                "You have not configured runserver to use ASGI.",
                hint="Add daphne to settings.py:INSTALLED_APPS.",
                id="reactpy_django.W012",
            )
        )

    # Removed REACTPY_RECONNECT_MAX setting
    if getattr(settings, "REACTPY_RECONNECT_MAX", None):
        warnings.append(
            Warning(
                "REACTPY_RECONNECT_MAX has been removed.",
                hint="See the docs for the new REACTPY_RECONNECT_* settings.",
                id="reactpy_django.W013",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_INTERVAL, int)
        and config.REACTPY_RECONNECT_INTERVAL > 30000
    ):
        warnings.append(
            Warning(
                "REACTPY_RECONNECT_INTERVAL is set to >30 seconds. Are you sure this is intentional? "
                "This may cause unexpected delays between reconnection.",
                hint="Check your value for REACTPY_RECONNECT_INTERVAL or suppress this warning.",
                id="reactpy_django.W014",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_MAX_RETRIES, int)
        and config.REACTPY_RECONNECT_MAX_RETRIES > 5000
    ):
        warnings.append(
            Warning(
                "REACTPY_RECONNECT_MAX_RETRIES is set to a very large value. Are you sure this is intentional? "
                "This may leave your clients attempting reconnections for a long time.",
                hint="Check your value for REACTPY_RECONNECT_MAX_RETRIES or suppress this warning.",
                id="reactpy_django.W015",
            )
        )

    # Check if the value is too large (greater than 50)
    if (
        isinstance(config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER, (int, float))
        and config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER > 100
    ):
        warnings.append(
            Warning(
                "REACTPY_RECONNECT_BACKOFF_MULTIPLIER is set to a very large value. Are you sure this is intentional?",
                hint="Check your value for REACTPY_RECONNECT_BACKOFF_MULTIPLIER or suppress this warning.",
                id="reactpy_django.W016",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_MAX_INTERVAL, int)
        and isinstance(config.REACTPY_RECONNECT_INTERVAL, int)
        and isinstance(config.REACTPY_RECONNECT_MAX_RETRIES, int)
        and isinstance(config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER, (int, float))
        and config.REACTPY_RECONNECT_INTERVAL > 0
        and config.REACTPY_RECONNECT_MAX_INTERVAL > 0
        and config.REACTPY_RECONNECT_MAX_RETRIES > 0
        and config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER > 1
        and (
            config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER
            ** config.REACTPY_RECONNECT_MAX_RETRIES
        )
        * config.REACTPY_RECONNECT_INTERVAL
        < config.REACTPY_RECONNECT_MAX_INTERVAL
    ):
        max_value = math.floor(
            (
                config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER
                ** config.REACTPY_RECONNECT_MAX_RETRIES
            )
            * config.REACTPY_RECONNECT_INTERVAL
        )
        warnings.append(
            Warning(
                "Your current ReactPy configuration can never reach REACTPY_RECONNECT_MAX_INTERVAL. At most you will reach "
                f"{max_value} miliseconds, which is less than {config.REACTPY_RECONNECT_MAX_INTERVAL} (REACTPY_RECONNECT_MAX_INTERVAL).",
                hint="Check your ReactPy REACTPY_RECONNECT_* settings.",
                id="reactpy_django.W017",
            )
        )

    position_to_beat = 0
    for app in INSTALLED_APPS:
        if app.startswith("django.contrib."):
            position_to_beat = INSTALLED_APPS.index(app)
    if (
        "reactpy_django" in INSTALLED_APPS
        and INSTALLED_APPS.index("reactpy_django") < position_to_beat
    ):
        warnings.append(
            Warning(
                "The position of 'reactpy_django' in INSTALLED_APPS is suspicious.",
                hint="Move 'reactpy_django' below all 'django.contrib.*' apps, or suppress this warning.",
                id="reactpy_django.W018",
            )
        )

    return warnings


@register(Tags.compatibility)
def reactpy_errors(app_configs, **kwargs):
    from django.conf import settings

    from reactpy_django import config

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
    if not isinstance(getattr(settings, "REACTPY_URL_PREFIX", ""), str):
        errors.append(
            Error(
                "Invalid type for REACTPY_URL_PREFIX.",
                hint="REACTPY_URL_PREFIX should be a string.",
                obj=settings.REACTPY_URL_PREFIX,
                id="reactpy_django.E003",
            )
        )
    if not isinstance(getattr(settings, "REACTPY_SESSION_MAX_AGE", 0), int):
        errors.append(
            Error(
                "Invalid type for REACTPY_SESSION_MAX_AGE.",
                hint="REACTPY_SESSION_MAX_AGE should be an integer.",
                obj=settings.REACTPY_SESSION_MAX_AGE,
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
        getattr(settings, "REACTPY_DEFAULT_QUERY_POSTPROCESSOR", ""), (str, type(None))
    ):
        errors.append(
            Error(
                "Invalid type for REACTPY_DEFAULT_QUERY_POSTPROCESSOR.",
                hint="REACTPY_DEFAULT_QUERY_POSTPROCESSOR should be a string or None.",
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

    # DELETED E009: Check if `channels` is in INSTALLED_APPS

    if not isinstance(getattr(settings, "REACTPY_DEFAULT_HOSTS", []), list):
        errors.append(
            Error(
                "Invalid type for REACTPY_DEFAULT_HOSTS.",
                hint="REACTPY_DEFAULT_HOSTS should be a list.",
                obj=settings.REACTPY_DEFAULT_HOSTS,
                id="reactpy_django.E010",
            )
        )

    # Check of all values in the list are strings
    if isinstance(getattr(settings, "REACTPY_DEFAULT_HOSTS", None), list):
        for host in settings.REACTPY_DEFAULT_HOSTS:
            if not isinstance(host, str):
                errors.append(
                    Error(
                        f"Invalid type {type(host)} within REACTPY_DEFAULT_HOSTS.",
                        hint="REACTPY_DEFAULT_HOSTS should be a list of strings.",
                        obj=settings.REACTPY_DEFAULT_HOSTS,
                        id="reactpy_django.E011",
                    )
                )
                break

    if not isinstance(config.REACTPY_RECONNECT_INTERVAL, int):
        errors.append(
            Error(
                "Invalid type for REACTPY_RECONNECT_INTERVAL.",
                hint="REACTPY_RECONNECT_INTERVAL should be an integer.",
                id="reactpy_django.E012",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_INTERVAL, int)
        and config.REACTPY_RECONNECT_INTERVAL < 0
    ):
        errors.append(
            Error(
                "Invalid value for REACTPY_RECONNECT_INTERVAL.",
                hint="REACTPY_RECONNECT_INTERVAL should be a positive integer.",
                id="reactpy_django.E013",
            )
        )

    if not isinstance(config.REACTPY_RECONNECT_MAX_INTERVAL, int):
        errors.append(
            Error(
                "Invalid type for REACTPY_RECONNECT_MAX_INTERVAL.",
                hint="REACTPY_RECONNECT_MAX_INTERVAL should be an integer.",
                id="reactpy_django.E014",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_MAX_INTERVAL, int)
        and config.REACTPY_RECONNECT_MAX_INTERVAL < 0
    ):
        errors.append(
            Error(
                "Invalid value for REACTPY_RECONNECT_MAX_INTERVAL.",
                hint="REACTPY_RECONNECT_MAX_INTERVAL should be a positive integer.",
                id="reactpy_django.E015",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_MAX_INTERVAL, int)
        and isinstance(config.REACTPY_RECONNECT_INTERVAL, int)
        and config.REACTPY_RECONNECT_MAX_INTERVAL < config.REACTPY_RECONNECT_INTERVAL
    ):
        errors.append(
            Error(
                "REACTPY_RECONNECT_MAX_INTERVAL is less than REACTPY_RECONNECT_INTERVAL.",
                hint="REACTPY_RECONNECT_MAX_INTERVAL should be greater than or equal to REACTPY_RECONNECT_INTERVAL.",
                id="reactpy_django.E016",
            )
        )

    if not isinstance(config.REACTPY_RECONNECT_MAX_RETRIES, int):
        errors.append(
            Error(
                "Invalid type for REACTPY_RECONNECT_MAX_RETRIES.",
                hint="REACTPY_RECONNECT_MAX_RETRIES should be an integer.",
                id="reactpy_django.E017",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_MAX_RETRIES, int)
        and config.REACTPY_RECONNECT_MAX_RETRIES < 0
    ):
        errors.append(
            Error(
                "Invalid value for REACTPY_RECONNECT_MAX_RETRIES.",
                hint="REACTPY_RECONNECT_MAX_RETRIES should be a positive integer.",
                id="reactpy_django.E018",
            )
        )

    if not isinstance(config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER, (int, float)):
        errors.append(
            Error(
                "Invalid type for REACTPY_RECONNECT_BACKOFF_MULTIPLIER.",
                hint="REACTPY_RECONNECT_BACKOFF_MULTIPLIER should be an integer or float.",
                id="reactpy_django.E019",
            )
        )

    if (
        isinstance(config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER, (int, float))
        and config.REACTPY_RECONNECT_BACKOFF_MULTIPLIER < 1
    ):
        errors.append(
            Error(
                "Invalid value for REACTPY_RECONNECT_BACKOFF_MULTIPLIER.",
                hint="REACTPY_RECONNECT_BACKOFF_MULTIPLIER should be greater than or equal to 1.",
                id="reactpy_django.E020",
            )
        )

    if not isinstance(config.REACTPY_PRERENDER, bool):
        errors.append(
            Error(
                "Invalid type for REACTPY_PRERENDER.",
                hint="REACTPY_PRERENDER should be a boolean.",
                id="reactpy_django.E021",
            )
        )

    if not isinstance(config.REACTPY_AUTO_RELOGIN, bool):
        errors.append(
            Error(
                "Invalid type for REACTPY_AUTO_RELOGIN.",
                hint="REACTPY_AUTO_RELOGIN should be a boolean.",
                id="reactpy_django.E022",
            )
        )

    return errors
