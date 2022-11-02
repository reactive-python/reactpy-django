???+ summary

    Django IDOM uses your **Django project's** `settings.py` file to modify the behavior of IDOM.

## Primary Configuration

=== "settings.py"

    <!--settings-start-->

    ```python linenums="1"
    # If "idom" cache is not configured, then we will use "default" instead
    CACHES = {
    "idom": {"BACKEND": ...},
    }

    # Maximum seconds between two reconnection attempts that would cause the client give up.
    # 0 will disable reconnection.
    IDOM_WS_MAX_RECONNECT_TIMEOUT = 604800

    # The URL for IDOM to serve websockets
    IDOM_WEBSOCKET_URL = "idom/"
    ```

    <!--settings-end-->

??? question "Do I need to modify my settings?"

    The default configuration of IDOM is adequate for the majority of use cases.

    You should only consider changing settings when the necessity arises.
