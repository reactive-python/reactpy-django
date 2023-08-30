## Overview

<p class="intro" markdown>

Your **Django project's** `settings.py` can modify the behavior of ReactPy.

</p>

!!! note

    The default configuration of ReactPy is suitable for the vast majority of use cases.

    You should only consider changing settings when the necessity arises.

---

## Primary Configuration

<!--config-details-start-->

These are ReactPy-Django's default settings values. You can modify these values in your **Django project's** `settings.py` to change the behavior of ReactPy.

| Setting | Default Value | Example Value(s) | Description |
| --- | --- | --- | --- |
| `REACTPY_CACHE` | `#!python "default"` | `#!python "my-reactpy-cache"` | Cache used to store ReactPy web modules. ReactPy benefits from a fast, well indexed cache.<br/>We recommend installing [`redis`](https://redis.io/) or [`python-diskcache`](https://grantjenks.com/docs/diskcache/tutorial.html#djangocache). |
| `REACTPY_DATABASE` | `#!python "default"` | `#!python "my-reactpy-database"` | Database used to store ReactPy session data. ReactPy requires a multiprocessing-safe and thread-safe database.<br/>If configuring `REACTPY_DATABASE`, it is mandatory to use our database router like such:<br/>`#!python DATABASE_ROUTERS = ["reactpy_django.database.Router", ...]` |
| `REACTPY_SESSION_MAX_AGE` | `#!python 259200` | `#!python 0`, `#!python 60`, `#!python 96000` | Maximum seconds to store ReactPy session data, such as `args` and `kwargs` passed into your component template tag.<br/>Use `#!python 0` to not store any session data. |
| `REACTPY_URL_PREFIX` | `#!python "reactpy/"` | `#!python "rp/"`, `#!python "render/reactpy/"` | The prefix to be used for all ReactPy websocket and HTTP URLs. |
| `REACTPY_DEFAULT_QUERY_POSTPROCESSOR` | `#!python "reactpy_django.utils.django_query_postprocessor"` | `#!python None`, `#!python "example_project.my_query_postprocessor"` | Dotted path to the default `reactpy_django.hooks.use_query` postprocessor function. Postprocessor functions can be async or sync, and the parameters must contain the arg `#!python data`. Set `REACTPY_DEFAULT_QUERY_POSTPROCESSOR` to `#!python None` to globally disable the default postprocessor. |
| `REACTPY_AUTH_BACKEND` | `#!python "django.contrib.auth.backends.ModelBackend"` | `#!python "example_project.auth.MyModelBackend"` | Dotted path to the Django authentication backend to use for ReactPy components. This is only needed if:<br/> 1. You are using `AuthMiddlewareStack` and...<br/> 2. You are using Django's `AUTHENTICATION_BACKENDS` setting and...<br/> 3. Your Django user model does not define a `backend` attribute. |
| `REACTPY_BACKHAUL_THREAD` | `#!python False` | `#!python True` | Whether to render ReactPy components in a dedicated thread. This allows the webserver to process web traffic while during ReactPy rendering.<br/>Vastly improves throughput with web servers such as `hypercorn` and `uvicorn`. |
| `REACTPY_DEFAULT_HOSTS` | `#!python None` | `#!python ["localhost:8000", "localhost:8001", "localhost:8002/subdir" ]` | The default host(s) that can render your ReactPy components. ReactPy will use these hosts in a round-robin fashion, allowing for easy distributed computing.<br/>You can use the `host` argument in your [template tag](../features/template-tag.md#component) as a manual override. |
| `REACTPY_RECONNECT_INTERVAL` | `#!python 750` | `#!python 100`, `#!python 2500`, `#!python 6000` | Milliseconds between client reconnection attempts. This value will gradually increase if `REACTPY_RECONNECT_BACKOFF_MULTIPLIER` is greater than `#!python 1`. |
| `REACTPY_RECONNECT_MAX_INTERVAL` | `#!python 60000` | `#!python 10000`, `#!python 25000`, `#!python 900000` | Maximum milliseconds between client reconnection attempts. This allows setting an upper bound on how high `REACTPY_RECONNECT_BACKOFF_MULTIPLIER` can increase the time between reconnection attempts. |
| `REACTPY_RECONNECT_MAX_RETRIES` | `#!python 150` | `#!python 0`, `#!python 5`, `#!python 300` | Maximum number of reconnection attempts before the client gives up. |
| `REACTPY_RECONNECT_BACKOFF_MULTIPLIER` | `#!python 1.25` | `#!python 1`, `#!python 1.5`, `#!python 3` | Multiplier for the time between client reconnection attempts. On each reconnection attempt, the `REACTPY_RECONNECT_INTERVAL` will be multiplied by this to increase the time between attempts. You can keep time between each reconnection the same by setting this to `#!python 1`. |

<!--config-details-end-->
