# IDOM works best with a multiprocessing-safe and thread-safe cache backend.
IDOM_CACHE = "default"

# IDOM works best with a multiprocessing-safe and thread-safe database backend.
IDOM_DATABASE = "default"

# Maximum seconds between reconnection attempts before giving up.
# Use `0` to prevent component reconnection.
IDOM_RECONNECT_MAX = 259200

# The URL for IDOM to serve the component rendering websocket
IDOM_WEBSOCKET_URL = "idom/"

# Dotted path to the default postprocessor function, or `None`
IDOM_DEFAULT_QUERY_POSTPROCESSOR = "example_project.utils.my_postprocessor"