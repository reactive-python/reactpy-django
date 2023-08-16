# Cache used to store ReactPy web modules.
# ReactPy benefits from a fast, well indexed cache.
# We recommend redis or python-diskcache.
REACTPY_CACHE = "default"

# Database ReactPy uses to store session data.
# ReactPy requires a multiprocessing-safe and thread-safe database.
# Configuring Django's DATABASE_ROUTERS setting is mandatory if using REACTPY_DATABASE.
REACTPY_DATABASE = "default"
DATABASE_ROUTERS = ["reactpy_django.database.Router", ...]

# Maximum seconds between reconnection attempts before giving up.
# Use `0` to prevent component reconnection.
REACTPY_RECONNECT_MAX = 259200

# The prefix to be used for all ReactPy API URLs.
REACTPY_URL_PREFIX = "reactpy/"

# Dotted path to the default `reactpy_django.hooks.use_query` postprocessor function.
REACTPY_DEFAULT_QUERY_POSTPROCESSOR = "reactpy_django.utils.django_query_postprocessor"

# Dotted path to the Django authentication backend to use for ReactPy components.
# This is only needed if:
#   1. You are using `AuthMiddlewareStack` and...
#   2. You are using Django's `AUTHENTICATION_BACKENDS` setting and...
#   3. Your Django user model does not define a `backend` attribute
REACTPY_AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"

# Whether to enable rendering ReactPy via a dedicated backhaul thread.
# This allows the webserver to process traffic while during ReactPy rendering.
REACTPY_BACKHAUL_THREAD = False
