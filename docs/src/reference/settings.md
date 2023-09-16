## Overview

<p class="intro" markdown>

<!--intro-start-->

These are ReactPy-Django's default settings values. You can modify these values in your **Django project's** `settings.py` to change the behavior of ReactPy.

<!--intro-end-->

</p>

!!! note

    The default configuration of ReactPy is suitable for the vast majority of use cases.

    You should only consider changing settings when the necessity arises.

---

<!--config-table-start-->

## General Settings

| Setting | Default Value | Example Value(s) | Description |
| --- | --- | --- | --- |
| `#!python REACTPY_URL_PREFIX` | `#!python "reactpy/"` | `#!python "rp/"`, `#!python "render/reactpy/"` | The prefix used for all ReactPy WebSocket and HTTP URLs. |
| `#!python REACTPY_DEFAULT_QUERY_POSTPROCESSOR` | `#!python "reactpy_django.utils.django_query_postprocessor"` | `#!python "example_project.postprocessor"`, `#!python None` | Dotted path to the default `#!python reactpy_django.hooks.use_query` postprocessor function. Postprocessor functions can be async or sync, and the function must contain a `#!python data` parameter. Set `#!python REACTPY_DEFAULT_QUERY_POSTPROCESSOR` to `#!python None` to globally disable the default postprocessor. |
| `#!python REACTPY_AUTH_BACKEND` | `#!python "django.contrib.auth.backends.ModelBackend"` | `#!python "example_project.auth.MyModelBackend"` | Dotted path to the Django authentication backend to use for ReactPy components. This is only needed if:<br/> 1. You are using `#!python AuthMiddlewareStack` and...<br/> 2. You are using Django's `#!python AUTHENTICATION_BACKENDS` setting and...<br/> 3. Your Django user model does not define a `#!python backend` attribute. |

## Performance Settings

| Setting | Default Value | Example Value(s) | Description |
| --- | --- | --- | --- |
| `#!python REACTPY_DATABASE` | `#!python "default"` | `#!python "my-reactpy-database"` | Multiprocessing-safe database used to store ReactPy session data. If configuring `#!python REACTPY_DATABASE`, it is mandatory to enable our database router like such:<br/>`#!python DATABASE_ROUTERS = ["reactpy_django.database.Router", ...]` |
| `#!python REACTPY_CACHE` | `#!python "default"` | `#!python "my-reactpy-cache"` | Cache used for ReactPy JavaScript modules. We recommend installing [`redis`](https://redis.io/) or [`python-diskcache`](https://grantjenks.com/docs/diskcache/tutorial.html#djangocache). |
| `#!python REACTPY_BACKHAUL_THREAD` | `#!python False` | `#!python True` | Configures whether ReactPy components are rendered in a dedicated thread. This allows the web server to process traffic during ReactPy rendering. Vastly improves throughput with web servers such as [`hypercorn`](https://pgjones.gitlab.io/hypercorn/) and [`uvicorn`](https://www.uvicorn.org/). |
| `#!python REACTPY_DEFAULT_HOSTS` | `#!python None` | `#!python ["localhost:8000", "localhost:8001", "localhost:8002/subdir"]` | The default host(s) that can render your ReactPy components. ReactPy will use these hosts in a round-robin fashion, allowing for easy distributed computing. You can use the `#!python host` argument in your [template tag](../reference/template-tag.md#component) as a manual override. |
| `#!python REACTPY_PRERENDER` | `#!python False` | `#!python True` | Configures whether to pre-render your components, which enables SEO compatibility and increases perceived responsiveness. You can use the `#!python prerender` argument in your [template tag](../reference/template-tag.md#component) as a manual override. During pre-rendering, there are some key differences in behavior:<br/> 1. Only the component's first render is pre-rendered.<br/> 2. All `#!python connection` related hooks use HTTP.<br/> 3. `#!python html.script` is executed during both pre-render and render.<br/> 4. Component is non-interactive until a WebSocket connection is formed. |

## Stability Settings

| Setting | Default Value | Example Value(s) | Description |
| --- | --- | --- | --- |
| `#!python REACTPY_RECONNECT_INTERVAL` | `#!python 750` | `#!python 100`, `#!python 2500`, `#!python 6000` | Milliseconds between client reconnection attempts. |
| `#!python REACTPY_RECONNECT_BACKOFF_MULTIPLIER` | `#!python 1.25` | `#!python 1`, `#!python 1.5`, `#!python 3` | On each reconnection attempt, the `#!python REACTPY_RECONNECT_INTERVAL` will be multiplied by this value to increase the time between attempts. You can keep time between each reconnection the same by setting this to `#!python 1`. |
| `#!python REACTPY_RECONNECT_MAX_INTERVAL` | `#!python 60000` | `#!python 10000`, `#!python 25000`, `#!python 900000` | Maximum milliseconds between client reconnection attempts. This allows setting an upper bound on how high `#!python REACTPY_RECONNECT_BACKOFF_MULTIPLIER` can increase the time between reconnection attempts. |
| `#!python REACTPY_RECONNECT_MAX_RETRIES` | `#!python 150` | `#!python 0`, `#!python 5`, `#!python 300` | Maximum number of reconnection attempts before the client gives up. |
| `#!python REACTPY_SESSION_MAX_AGE` | `#!python 259200` | `#!python 0`, `#!python 60`, `#!python 96000` | Maximum seconds to store ReactPy component sessions. This includes data such as `#!python *args` and `#!python **kwargs` passed into your component template tag. Use `#!python 0` to not store any session data. |

<!--config-table-end-->
