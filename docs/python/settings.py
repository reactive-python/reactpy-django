# ReactPy requires a multiprocessing-safe and thread-safe cache.
REACTPY_CACHE = "default"

# ReactPy requires a multiprocessing-safe and thread-safe database.
REACTPY_DATABASE = "default"

# Maximum seconds between reconnection attempts before giving up.
# Use `0` to prevent component reconnection.
REACTPY_RECONNECT_MAX = 259200

# The URL for ReactPy to serve the component rendering websocket
REACTPY_WEBSOCKET_URL = "reactpy/"

# Dotted path to the default `reactpy_django.hooks.use_query` postprocessor function, or `None`
REACTPY_DEFAULT_QUERY_POSTPROCESSOR = "reactpy_django.utils.django_query_postprocessor"
