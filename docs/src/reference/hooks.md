## Overview

<p class="intro" markdown>

Prefabricated hooks can be used within your `components.py` to help simplify development.

</p>

!!! abstract "Note"

    Looking for standard React hooks?

    This package only contains Django specific hooks. Standard hooks can be found within [`reactive-python/reactpy`](https://reactpy.dev/docs/reference/hooks-api.html#basic-hooks).

---

## Use Query

This hook is used [read](https://www.sumologic.com/glossary/crud/) data from the Django ORM.

The query function you provide must return either a `#!python Model` or `#!python QuerySet`.

=== "components.py"

    ```python
    {% include "../../python/use-query.py" %}
    ```

=== "models.py"

    ```python
    {% include "../../python/example/models.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python options` | `#!python QueryOptions | None` | An optional `#!python QueryOptions` object that can modify how the query is executed. | `#!python None` |
    | `#!python query` | `#!python Callable[_Params, _Result | None]` | A callable that returns a Django `#!python Model` or `#!python QuerySet`. | N/A |
    | `#!python *args` | `#!python _Params.args` | Positional arguments to pass into `#!python query`. | N/A |
    | `#!python **kwargs` | `#!python _Params.kwargs` | Keyword arguments to pass into `#!python query`. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Query[_Result | None]` | An object containing `#!python loading`/`#!python error` states, your `#!python data` (if the query has successfully executed), and a `#!python refetch` callable that can be used to re-run the query. |

??? question "How can I provide arguments to my query function?"

    `#!python *args` and `#!python **kwargs` can be provided to your query function via `#!python use_query` parameters.

    === "components.py"

        ```python
        {% include "../../python/use-query-args.py" %}
        ```

??? question "Why does `#!python get_items` in the example return `#!python TodoItem.objects.all()`?"

    This was a technical design decision to based on [Apollo's `#!javascript useQuery` hook](https://www.apollographql.com/docs/react/data/queries/), but ultimately helps avoid Django's `#!python SynchronousOnlyOperation` exceptions.

    The `#!python use_query` hook ensures the provided `#!python Model` or `#!python QuerySet` executes all [deferred](https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.get_deferred_fields)/[lazy queries](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy) safely prior to reaching your components.

??? question "How can I use `#!python QueryOptions` to customize fetching behavior?"

    <font size="4">**`#!python thread_sensitive`**</font>

    Whether to run your synchronous query function in thread-sensitive mode. Thread-sensitive mode is turned on by default due to Django ORM limitations. See Django's [`#!python sync_to_async` docs](https://docs.djangoproject.com/en/dev/topics/async/#sync-to-async) docs for more information.

    This setting only applies to sync query functions, and will be ignored for async functions.

    === "components.py"

        ```python
        {% include "../../python/use-query-thread-sensitive.py" %}
        ```

    ---

    <font size="4">**`#!python postprocessor`**</font>

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you...

    1. Want to use this hook to defer IO intensive tasks to be computed in the background
    2. Want to to utilize `#!python use_query` with a different ORM

    ... then you can either set a custom `#!python postprocessor`, or disable all postprocessing behavior by modifying the `#!python QueryOptions.postprocessor` parameter. In the example below, we will set the `#!python postprocessor` to `#!python None` to disable postprocessing behavior.

    === "components.py"

        ```python
        {% include "../../python/use-query-postprocessor-disable.py" %}
        ```

    If you wish to create a custom `#!python postprocessor`, you will need to create a callable.

    The first argument of `#!python postprocessor` must be the query `#!python data`. All proceeding arguments
    are optional `#!python postprocessor_kwargs` (see below). This `#!python postprocessor` must return
    the modified `#!python data`.

    === "components.py"

        ```python
        {% include "../../python/use-query-postprocessor-change.py" %}
        ```

    ---

    <font size="4">**`#!python postprocessor_kwargs`**</font>

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you have deep nested trees of relational data, this may not be a desirable behavior. In these scenarios, you may prefer to manually fetch these relational fields using a second `#!python use_query` hook.

    You can disable the prefetching behavior of the default `#!python postprocessor` (located at `#!python reactpy_django.utils.django_query_postprocessor`) via the `#!python QueryOptions.postprocessor_kwargs` parameter.

    === "components.py"

        ```python
        {% include "../../python/use-query-postprocessor-kwargs.py" %}
        ```

    _Note: In Django's ORM design, the field name to access foreign keys is [postfixed with `_set`](https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/) by default._

??? question "Can I define async query functions?"

    Async functions are supported by `#!python use_query`. You can use them in the same way as a sync query function.

    However, be mindful of Django async ORM restrictions.

    === "components.py"

        ```python
        {% include "../../python/use-query-async.py" %}
        ```

??? question "Can I make ORM calls without hooks?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

## Use Mutation

This hook is used to [create, update, or delete](https://www.sumologic.com/glossary/crud/) Django ORM objects.

The mutation function you provide should have no return value.

=== "components.py"

    ```python
    {% include "../../python/use-mutation.py" %}
    ```

=== "models.py"

    ```python
    {% include "../../python/example/models.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python mutate` | `#!python Callable[_Params, bool | None]` | A callable that performs Django ORM create, update, or delete functionality. If this function returns `#!python False`, then your `#!python refetch` function will not be used. | N/A |
    | `#!python refetch` | `#!python Callable[..., Any] | Sequence[Callable[..., Any]] | None` | A `#!python query` function (used by the `#!python use_query` hook) or a sequence of `#!python query` functions that will be called if the mutation succeeds. This is useful for refetching data after a mutation has been performed. | `#!python None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Mutation[_Params]` | An object containing `#!python loading`/`#!python error` states, a `#!python reset` callable that will set `#!python loading`/`#!python error` states to defaults, and a `#!python execute` callable that will run the query. |

??? question "How can I provide arguments to my mutation function?"

    `#!python *args` and `#!python **kwargs` can be provided to your mutation function via #!python mutation.execute` parameters.

    === "components.py"

        ```python
        {% include "../../python/use-mutation-args-kwargs.py" %}
        ```

??? question "Can `#!python use_mutation` trigger a refetch of `#!python use_query`?"

    Yes, `#!python use_mutation` can queue a refetch of a `#!python use_query` via the `#!python refetch=...` argument.

    The example below is a merge of the `#!python use_query` and `#!python use_mutation` examples above with the addition of a `#!python use_mutation(refetch=...)` argument.

    Please note that any `#!python use_query` hooks that use `#!python get_items` will be refetched upon a successful mutation.

    === "components.py"

        ```python
        {% include "../../python/use-mutation-query-refetch.py" %}
        ```

    === "models.py"

        ```python
        {% include "../../python/example/models.py" %}
        ```

??? question "Can I make a failed `#!python use_mutation` try again?"

    Yes, a `#!python use_mutation` can be re-performed by calling `#!python reset()` on your `#!python use_mutation` instance.

    For example, take a look at `#!python reset_event` below.

    === "components.py"

        ```python
        {% include "../../python/use-mutation-reset.py" %}
        ```

    === "models.py"

        ```python
        {% include "../../python/example/models.py" %}
        ```

??? question "Can I make ORM calls without hooks?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

## Use Connection

This hook is used to fetch the Django Channels [WebSocket](https://channels.readthedocs.io/en/stable/topics/consumers.html#asyncjsonwebsocketconsumer).

=== "components.py"

    ```python
    {% include "../../python/use-connection.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Connection` | The component's WebSocket. |

## Use Scope

This is a shortcut that returns the WebSocket's [`#!python scope`](https://channels.readthedocs.io/en/stable/topics/consumers.html#scope).

=== "components.py"

    ```python
    {% include "../../python/use-scope.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python MutableMapping[str, Any]` | The WebSocket's `#!python scope`. |

## Use Location

This is a shortcut that returns the WebSocket's `#!python path`.

You can expect this hook to provide strings such as `/reactpy/my_path`.

=== "components.py"

    ```python
    {% include "../../python/use-location.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Location` | An object containing the current URL's `#!python pathname` and `#!python search` query. |

??? info "This hook's behavior will be changed in a future update"

    This hook will be updated to return the browser's currently active HTTP path. This change will come in alongside ReactPy URL routing support.

    Check out [reactive-python/reactpy-django#147](https://github.com/reactive-python/reactpy-django/issues/147) for more information.

## Use Origin

This is a shortcut that returns the WebSocket's `#!python origin`.

You can expect this hook to provide strings such as `http://example.com`.

=== "components.py"

    ```python
    {% include "../../python/use-origin.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python str | None` | A string containing the browser's current origin, obtained from WebSocket headers (if available). |
