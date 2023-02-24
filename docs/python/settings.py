# IDOM requires a multiprocessing-safe and thread-safe cache.
IDOM_CACHE = "default"

# IDOM requires a multiprocessing-safe and thread-safe database.
IDOM_DATABASE = "default"

# Maximum seconds between reconnection attempts before giving up.
# Use `0` to prevent component reconnection.
IDOM_RECONNECT_MAX = 259200

# The URL for IDOM to serve the component rendering websocket
IDOM_WEBSOCKET_URL = "idom/"

# Dotted path to the default `django_idom.hooks.use_query` postprocessor function, or `None`
IDOM_DEFAULT_QUERY_POSTPROCESSOR = "django_idom.utils.django_query_postprocessor"
