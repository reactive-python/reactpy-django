## Overview

!!! summary "Overview"

    Your **Django project's** `settings.py` can modify the behavior of ReactPy.

## Primary Configuration

<!--config-details-start-->

These are ReactPy-Django's default settings values. You can modify these values in your **Django project's** `settings.py` to change the behavior of ReactPy.

| Setting | Default Value | Example Value(s) | Description |
| --- | --- | --- | --- |
| `REACTPY_CACHE` | `#!python "default"` | `#!python "my-reactpy-cache"` | Cache used to store ReactPy web modules. ReactPy benefits from a fast, well indexed cache.<br/>We recommend installing [`redis`](https://redis.io/) or [`python-diskcache`](https://grantjenks.com/docs/diskcache/tutorial.html#djangocache). |
| `REACTPY_DATABASE` | `#!python "default"` | `#!python "my-reactpy-database"` | Database ReactPy uses to store session data. ReactPy requires a multiprocessing-safe and thread-safe database.<br/>If configuring `REACTPY_DATABASE`, it is mandatory to also configure `DATABASE_ROUTERS` like such:<br/>`#!python DATABASE_ROUTERS = ["reactpy_django.database.Router", ...]` |
| `REACTPY_RECONNECT_MAX` | `#!python 259200` | `#!python 96000`, `#!python 60`, `#!python 0` | Maximum seconds between reconnection attempts before giving up.<br/>Use `#!python 0` to prevent reconnection. |
| `REACTPY_URL_PREFIX` | `#!python "reactpy/"` | `#!python "rp/"`, `#!python "render/reactpy/"` | The prefix to be used for all ReactPy websocket and HTTP URLs. |
| `REACTPY_DEFAULT_QUERY_POSTPROCESSOR` | `#!python "reactpy_django.utils.django_query_postprocessor"` | `#!python "example_project.my_query_postprocessor"` | Dotted path to the default `reactpy_django.hooks.use_query` postprocessor function. |
| `REACTPY_AUTH_BACKEND` | `#!python "django.contrib.auth.backends.ModelBackend"` | `#!python "example_project.auth.MyModelBackend"` | Dotted path to the Django authentication backend to use for ReactPy components. This is only needed if:<br/> 1. You are using `AuthMiddlewareStack` and...<br/> 2. You are using Django's `AUTHENTICATION_BACKENDS` setting and...<br/> 3. Your Django user model does not define a `backend` attribute. |
| `REACTPY_BACKHAUL_THREAD` | `#!python False` | `#!python True` | Whether to render ReactPy components in a dedicated thread. This allows the webserver to process web traffic while during ReactPy rendering.<br/>Vastly improves throughput with web servers such as `hypercorn` and `uvicorn`. |
| `REACTPY_DEFAULT_HOSTS` | `#!python None` | `#!python ["localhost:8000", "localhost:8001", "localhost:8002/subdir" ]` | Default host(s) to use for ReactPy components. ReactPy will use these hosts in a round-robin fashion, allowing for easy distributed computing.<br/>You can use the `host` argument in your [template tag](../features/template-tag.md#component) to override this default. |

<!--config-details-end-->

??? question "Do I need to modify my settings?"

    The default configuration of ReactPy is suitable for the majority of use cases.

    You should only consider changing settings when the necessity arises.
