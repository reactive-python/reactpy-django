## Overview

<p class="intro" markdown>

Prefabricated hooks can be used within your `components.py` to help simplify development.

</p>

!!! note

    Looking for standard React hooks?

    This package only contains Django specific hooks. Standard hooks can be found within [`reactive-python/reactpy`](https://reactpy.dev/docs/reference/hooks-api.html#basic-hooks).

---

## Use Query

The `use_query` hook is used fetch Django ORM queries.

The function you provide into this hook must return either a `Model` or `QuerySet`.

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
    | `options` | `QueryOptions | None` | An optional `QueryOptions` object that can modify how the query is executed. | None |
    | `query` | `Callable[_Params, _Result | None]` | A callable that returns a Django `Model` or `QuerySet`. | N/A |
    | `*args` | `_Params.args` | Positional arguments to pass into `query`. | N/A |
    | `**kwargs` | `_Params.kwargs` | Keyword arguments to pass into `query`. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Query[_Result | None]` | An object containing `loading`/`error` states, your `data` (if the query has successfully executed), and a `refetch` callable that can be used to re-run the query. |

??? question "How can I provide arguments to my query function?"

    `*args` and `**kwargs` can be provided to your query function via `use_query` parameters.

    === "components.py"

        ```python
        {% include "../../python/use-query-args.py" %}
        ```

??? question "Why does `get_items` in the example return `TodoItem.objects.all()`?"

    This was a technical design decision to based on [Apollo's `useQuery` hook](https://www.apollographql.com/docs/react/data/queries/), but ultimately helps avoid Django's `SynchronousOnlyOperation` exceptions.

    The `use_query` hook ensures the provided `Model` or `QuerySet` executes all [deferred](https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.get_deferred_fields)/[lazy queries](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy) safely prior to reaching your components.

??? question "How can I use `QueryOptions` to customize fetching behavior?"

    <font size="4">**`thread_sensitive`**</font>

    Whether to run your synchronous query function in thread-sensitive mode. Thread-sensitive mode is turned on by default due to Django ORM limitations. See Django's [`sync_to_async` docs](https://docs.djangoproject.com/en/dev/topics/async/#sync-to-async) docs for more information.

    This setting only applies to sync query functions, and will be ignored for async functions.

    === "components.py"

        ```python
        {% include "../../python/use-query-thread-sensitive.py" %}
        ```

    ---

    <font size="4">**`postprocessor`**</font>

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you...

    1. Want to use this hook to defer IO intensive tasks to be computed in the background
    2. Want to to utilize `use_query` with a different ORM

    ... then you can either set a custom `postprocessor`, or disable all postprocessing behavior by modifying the `QueryOptions.postprocessor` parameter. In the example below, we will set the `postprocessor` to `None` to disable postprocessing behavior.

    === "components.py"

        ```python
        {% include "../../python/use-query-postprocessor-disable.py" %}
        ```

    If you wish to create a custom `postprocessor`, you will need to create a callable.

    The first argument of `postprocessor` must be the query `data`. All proceeding arguments
    are optional `postprocessor_kwargs` (see below). This `postprocessor` must return
    the modified `data`.

    === "components.py"

        ```python
        {% include "../../python/use-query-postprocessor-change.py" %}
        ```

    ---

    <font size="4">**`postprocessor_kwargs`**</font>

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you have deep nested trees of relational data, this may not be a desirable behavior. In these scenarios, you may prefer to manually fetch these relational fields using a second `use_query` hook.

    You can disable the prefetching behavior of the default `postprocessor` (located at `reactpy_django.utils.django_query_postprocessor`) via the `QueryOptions.postprocessor_kwargs` parameter.

    === "components.py"

        ```python
        {% include "../../python/use-query-postprocessor-kwargs.py" %}
        ```

    _Note: In Django's ORM design, the field name to access foreign keys is [postfixed with `_set`](https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/) by default._

??? question "Can I define async query functions?"

    Async functions are supported by `use_query`. You can use them in the same way as a sync query function.

    However, be mindful of Django async ORM restrictions.

    === "components.py"

        ```python
        {% include "../../python/use-query-async.py" %}
        ```

??? question "Can I make ORM calls without hooks?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

## Use Mutation

The `use_mutation` hook is used to create, update, or delete Django ORM objects.

The function you provide into this hook will have no return value.

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
    | `mutate` | `Callable[_Params, bool | None]` | A callable that performs Django ORM create, update, or delete functionality. If this function returns `False`, then your `refetch` function will not be used. | N/A |
    | `refetch` | `Callable[..., Any] | Sequence[Callable[..., Any]] | None` | A `query` function (used by the `use_query` hook) or a sequence of `query` functions that will be called if the mutation succeeds. This is useful for refetching data after a mutation has been performed. | `None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Mutation[_Params]` | An object containing `loading`/`error` states, a `reset` callable that will set `loading`/`error` states to defaults, and a `execute` callable that will run the query. |

??? question "How can I provide arguments to my mutation function?"

    `*args` and `**kwargs` can be provided to your mutation function via `mutation.execute` parameters.

    === "components.py"

        ```python
        {% include "../../python/use-mutation-args-kwargs.py" %}
        ```

??? question "Can `use_mutation` trigger a refetch of `use_query`?"

    Yes, `use_mutation` can queue a refetch of a `use_query` via the `refetch=...` argument.

    The example below is a merge of the `use_query` and `use_mutation` examples above with the addition of a `refetch` argument on `use_mutation`.

    Please note that any `use_query` hooks that use `get_items` will be refetched upon a successful mutation.

    === "components.py"

        ```python
        {% include "../../python/use-mutation-query-refetch.py" %}
        ```

    === "models.py"

        ```python
        {% include "../../python/example/models.py" %}
        ```

??? question "Can I make a failed `use_mutation` try again?"

    Yes, a `use_mutation` can be re-performed by calling `reset()` on your `use_mutation` instance.

    For example, take a look at `reset_event` below.

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

You can fetch the Django Channels [websocket](https://channels.readthedocs.io/en/stable/topics/consumers.html#asyncjsonwebsocketconsumer) at any time by using `use_connection`.

=== "components.py"

    ```python
    {% include "../../python/use-connection.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Connection` | The component's websocket. |

## Use Scope

This is a shortcut that returns the Websocket's [`scope`](https://channels.readthedocs.io/en/stable/topics/consumers.html#scope).

=== "components.py"

    ```python
    {% include "../../python/use-scope.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `MutableMapping[str, Any]` | The websocket's `scope`. |

## Use Location

This is a shortcut that returns the Websocket's `path`.

You can expect this hook to provide strings such as `/reactpy/my_path`.

=== "components.py"

    ```python
    {% include "../../python/use-location.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Location` | A object containing the current URL's `pathname` and `search` query. |

??? info "This hook's behavior will be changed in a future update"

    This hook will be updated to return the browser's currently active path. This change will come in alongside ReactPy URL routing support.

    Check out [reactive-python/reactpy-router#2](https://github.com/idom-team/idom-router/issues/2) for more information.

## Use Origin

This is a shortcut that returns the Websocket's `origin`.

You can expect this hook to provide strings such as `http://example.com`.

=== "components.py"

    ```python
    {% include "../../python/use-origin.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `str | None` | A string containing the browser's current origin, obtained from websocket headers (if available). |
