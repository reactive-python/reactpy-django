## Overview

<p class="intro" markdown>

These are ReactPy-Django's default settings values. You can modify these values in your **Django project's** `settings.py` to change the behavior of ReactPy.

</p>

!!! abstract "Note"

    The default configuration of ReactPy is suitable for the vast majority of use cases.

    You should only consider changing settings when the necessity arises.

---

## General Settings

---

### `#!python REACTPY_URL_PREFIX`

**Default:** `#!python "reactpy/"`

**Example Value(s):** `#!python "rp/"`, `#!python "render/reactpy/"`

The prefix used for all ReactPy WebSocket and HTTP URLs.

---

### `#!python REACTPY_DEFAULT_QUERY_POSTPROCESSOR`

**Default:** `#!python "reactpy_django.utils.django_query_postprocessor"`

**Example Value(s):** `#!python "example_project.postprocessor"`, `#!python None`

Dotted path to the default `#!python reactpy_django.hooks.use_query` postprocessor function.

Postprocessor functions can be async or sync. Here is an example of a sync postprocessor function:

```python linenums="0"
def postprocessor(data):
    del data["foo"]
    return data
```

Set `#!python REACTPY_DEFAULT_QUERY_POSTPROCESSOR` to `#!python None` to disable the default postprocessor.

---

### `#!python REACTPY_AUTH_BACKEND`

**Default:** `#!python "django.contrib.auth.backends.ModelBackend"`

**Example Value(s):** `#!python "example_project.auth.MyModelBackend"`

Dotted path to the Django authentication backend to use for ReactPy components. This is only needed if:

1. You are using `#!python settings.py:REACTPY_AUTO_RELOGIN=True` and...
2. You are using `#!python AuthMiddlewareStack` and...
3. You are using Django's `#!python AUTHENTICATION_BACKENDS` setting and...
4. Your Django user model does not define a `#!python backend` attribute.

---

### `#!python REACTPY_AUTO_RELOGIN`

**Default:** `#!python False`

**Example Value(s):** `#!python True`

Enabling this will cause component WebSocket connections to automatically [re-login](https://channels.readthedocs.io/en/latest/topics/authentication.html#how-to-log-a-user-in-out) users that are already authenticated.

This is useful to continuously update `#!python last_login` timestamps and refresh the [Django login session](https://docs.djangoproject.com/en/dev/topics/http/sessions/).

---

## Performance Settings

---

### `#!python REACTPY_DATABASE`

**Default:** `#!python "default"`

**Example Value(s):** `#!python "my-reactpy-database"`

Multiprocessing-safe database used by ReactPy for database-backed hooks and features.

If configuring this value, it is mandatory to enable our database router like such:

=== "settings.py"

    ```python linenums="0"
    DATABASE_ROUTERS = ["reactpy_django.database.Router", ...]
    ```

---

### `#!python REACTPY_CACHE`

**Default:** `#!python "default"`

**Example Value(s):** `#!python "my-reactpy-cache"`

Cache used by ReactPy, typically for caching disk operations.

We recommend using [`redis`](https://docs.djangoproject.com/en/dev/topics/cache/#redis), [`memcache`](https://docs.djangoproject.com/en/dev/topics/cache/#memcached), or [`local-memory caching`](https://docs.djangoproject.com/en/dev/topics/cache/#local-memory-caching).

---

### `#!python REACTPY_BACKHAUL_THREAD`

**Default:** `#!python False`

**Example Value(s):** `#!python True`

Configures whether ReactPy components are rendered in a dedicated thread.

This allows the web server to process other traffic during ReactPy rendering. Vastly improves throughput with web servers such as [`hypercorn`](https://pgjones.gitlab.io/hypercorn/) and [`uvicorn`](https://www.uvicorn.org/).

This setting is incompatible with [`daphne`](https://github.com/django/daphne).

---

### `#!python REACTPY_DEFAULT_HOSTS`

**Default:** `#!python None`

**Example Value(s):** `#!python ["localhost:8000", "localhost:8001", "localhost:8002/subdir"]`

The default host(s) that can render your ReactPy components.

ReactPy will use these hosts in a round-robin fashion, allowing for easy distributed computing.

You can use the `#!python host` argument in your [template tag](../reference/template-tag.md#component) to manually override this default.

---

### `#!python REACTPY_PRERENDER`

**Default:** `#!python False`

**Example Value(s):** `#!python True`

Configures whether to pre-render your components via HTTP, which enables SEO compatibility and reduces perceived latency.

During pre-rendering, there are some key differences in behavior:

1. Only the component's first render is pre-rendered.
2. All [`connection` hooks](https://reactive-python.github.io/reactpy-django/latest/reference/hooks/#connection-hooks) will provide HTTP variants.
3. The component will be non-interactive until a WebSocket connection is formed.

<!-- TODO: The comment below will become true when ReactPy no longer strips scripts from the DOM -->
<!-- 4. `#!python html.script` elements are executed twice (pre-render and post-render). -->

You can use the `#!python prerender` argument in your [template tag](../reference/template-tag.md#component) to manually override this default.

---

## Stability Settings

---

### `#!python REACTPY_RECONNECT_INTERVAL`

**Default:** `#!python 750`

**Example Value(s):** `#!python 100`, `#!python 2500`, `#!python 6000`

Milliseconds between client reconnection attempts.

---

### `#!python REACTPY_RECONNECT_BACKOFF_MULTIPLIER`

**Default:** `#!python 1.25`

**Example Value(s):** `#!python 1`, `#!python 1.5`, `#!python 3`

On each reconnection attempt, the `#!python REACTPY_RECONNECT_INTERVAL` will be multiplied by this value to increase the time between attempts.

You can keep time between each reconnection the same by setting this to `#!python 1`.

---

### `#!python REACTPY_RECONNECT_MAX_INTERVAL`

**Default:** `#!python 60000`

**Example Value(s):** `#!python 10000`, `#!python 25000`, `#!python 900000`

Maximum milliseconds between client reconnection attempts.

This allows setting an upper bound on how high `#!python REACTPY_RECONNECT_BACKOFF_MULTIPLIER` can increase the time between reconnection attempts.

---

### `#!python REACTPY_RECONNECT_MAX_RETRIES`

**Default:** `#!python 150`

**Example Value(s):** `#!python 0`, `#!python 5`, `#!python 300`

Maximum number of reconnection attempts before the client gives up.

---

### `#!python REACTPY_SESSION_MAX_AGE`

**Default:** `#!python 259200`

**Example Value(s):** `#!python 0`, `#!python 60`, `#!python 96000`

Maximum seconds a ReactPy component session is valid for. Invalid sessions are deleted during [ReactPy clean up](#auto-clean-settings).

ReactPy sessions include data such as `#!python *args` and `#!python **kwargs` passed into your `#!jinja {% component %}` template tag.

Use `#!python 0` to not store any session data.

---

## Auto-Clean Settings

---

### `#!python REACTPY_CLEAN_INTERVAL`

**Default:** `#!python 604800`

**Example Value(s):** `#!python 0`, `#!python 3600`, `#!python 86400`, `#!python None`

Minimum seconds between ReactPy automatic clean up operations.

After a component disconnection, the server will perform a clean up if this amount of time has passed since the last clean up.

Set this value to `#!python None` to disable automatic clean up operations.

---

### `#!python REACTPY_CLEAN_SESSIONS`

**Default:** `#!python True`

**Example Value(s):** `#!python False`

Configures whether ReactPy should clean up expired component sessions during automatic clean up operations.

---

### `#!python REACTPY_CLEAN_USER_DATA`

**Default:** `#!python True`

**Example Value(s):** `#!python False`

Configures whether ReactPy should clean up orphaned user data during automatic clean up operations.

Typically, user data does not become orphaned unless the server crashes during a `#!python User` delete operation.
