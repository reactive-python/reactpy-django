# Cache used to store ReactPy web modules.
# ReactPy requires a multiprocessing-safe and thread-safe cache.
# We recommend redis or python-diskcache.
REACTPY_CACHE = "default"

# Database ReactPy uses to store session data.
# ReactPy requires a multiprocessing-safe and thread-safe database.
# DATABASE_ROUTERS is mandatory if REACTPY_DATABASE is configured.
REACTPY_DATABASE = "default"
DATABASE_ROUTERS = ["reactpy_django.database.Router", ...]

# Maximum seconds between reconnection attempts before giving up.
# Use `0` to prevent component reconnection.
REACTPY_RECONNECT_MAX = 259200

# The URL for ReactPy to serve the component rendering websocket.
REACTPY_WEBSOCKET_URL = "reactpy/"

# Dotted path to the default `reactpy_django.hooks.use_query` postprocessor function,
# or `None`.
REACTPY_DEFAULT_QUERY_POSTPROCESSOR = "reactpy_django.utils.django_query_postprocessor"

# Dotted path to the Django authentication backend to use for ReactPy components.
# This is only needed if:
#   1. You are using `AuthMiddlewareStack` and...
#   2. You are using Django's `AUTHENTICATION_BACKENDS` setting and...
#   3. Your Django user model does not define a `backend` attribute
REACTPY_AUTH_BACKEND = "django.contrib.auth.backends.ModelBackend"

# Whether to enable rendering ReactPy via a dedicated backhaul thread
# This allows the webserver to process traffic while during ReactPy rendering
REACTPY_BACKHAUL_THREAD = True
