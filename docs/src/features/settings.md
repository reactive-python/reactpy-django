???+ summary

    Django-IDOM uses your **Django project's** `settings.py` file to modify the behavior of IDOM.

## Primary Configuration

=== "settings.py"

    <!--settings-start-->

    ```python
    # If "idom" cache is not configured, then "default" will be used
    # IDOM expects a multiprocessing-safe and thread-safe cache backend.
    CACHES = {
    "idom": {"BACKEND": ...},
    }

    # Maximum seconds between reconnection attempts before giving up.
    # Use `0` to prevent component reconnection.
    IDOM_RECONNECT_MAX = 259200

    # The URL for IDOM to serve the component rendering websocket
    IDOM_WEBSOCKET_URL = "idom/"

    # Dotted path to the default postprocessor function, or `None`
    IDOM_DEFAULT_QUERY_POSTPROCESSOR = "example_project.utils.my_postprocessor"
    ```

    <!--settings-end-->

??? question "Do I need to modify my settings?"

    The default configuration of IDOM is adequate for the majority of use cases.

    You should only consider changing settings when the necessity arises.
