Django IDOM uses your **Django project's** `settings.py` file to modify some behaviors of IDOM.

Here are the configurable variables that are available.

<!--settings-start-->

```python title="settings.py"
# If "idom" cache is not configured, then we'll use "default" instead
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
