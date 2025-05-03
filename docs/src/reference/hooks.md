## Overview

<p class="intro" markdown>

Prefabricated hooks can be used within your `components.py` to help simplify development.

</p>

!!! abstract "Note"

    Looking for standard React hooks?

    This package only contains Django specific hooks. Standard hooks can be found within [`reactive-python/reactpy`](https://reactpy.dev/docs/reference/hooks-api.html#basic-hooks).

---

## Database Hooks

---

### Use Query

Execute functions in the background and return the result, typically to [read](https://www.sumologic.com/glossary/crud/) data from the Django ORM.

The [default postprocessor](./utils.md#django-query-postprocessor) expects your query function to `#!python return` a Django `#!python Model` or `#!python QuerySet`. This needs [to be changed](./settings.md#reactpy_default_query_postprocessor) or disabled to execute other types of queries.

Query functions can be sync or async.

=== "components.py"

    ```python
    {% include "../../examples/python/use_query.py" %}
    ```

=== "models.py"

    ```python
    {% include "../../examples/python/todo_item_model.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python query` | `#!python Callable[FuncParams, Awaitable[Inferred]] | Callable[FuncParams, Inferred]` | A function that executes a query and returns some data. | N/A |
    | `#!python kwargs` | `#!python dict[str, Any] | None` | Keyword arguments to passed into the `#!python query` function. | `#!python None` |
    | `#!python thread_sensitive` | `#!python bool` | Whether to run your query function in thread sensitive mode. This setting only applies to sync functions, and is turned on by default due to Django ORM limitations. | `#!python True` |
    | `#!python postprocessor` | `#!python AsyncPostprocessor | SyncPostprocessor | None` | A callable that processes the query `#!python data` before it is returned. The first argument of postprocessor function must be the query `#!python data`. All proceeding arguments are optional `#!python postprocessor_kwargs`. This postprocessor function must return the modified `#!python data`. | `#!python None` |
    | `#!python postprocessor_kwargs` | `#!python dict[str, Any] | None` | Keyworded arguments passed into the `#!python postprocessor` function. | `#!python None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Query[Inferred]` | An object containing `#!python loading`/`#!python error` states, your `#!python data` (if the query has successfully executed), and a `#!python refetch` callable that can be used to re-run the query. |

??? question "How can I provide arguments to my query function?"

    `#!python kwargs` can be provided to your query function via the `#!python kwargs=...` parameter.

    === "components.py"

        ```python
        {% include "../../examples/python/use_query_args.py" %}
        ```

??? question "How can I customize this hook's behavior?"

    This hook has several parameters that can be used to customize behavior.

    Below are examples of values that can be modified.

    ---

    <font size="4">**`#!python thread_sensitive`**</font>

    Whether to run your synchronous query function in thread sensitive mode. Thread sensitive mode is turned on by default due to Django ORM limitations. See Django's [`sync_to_async` docs](https://docs.djangoproject.com/en/stable/topics/async/#sync-to-async) docs for more information.

    This setting only applies to sync query functions, and will be ignored for async functions.

    === "components.py"

        ```python
        {% include "../../examples/python/use_query_thread_sensitive.py" %}
        ```

    ---

    <font size="4">**`#!python postprocessor`**</font>

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you...

    1. Want to use this hook to defer IO intensive tasks to be computed in the background
    2. Want to to utilize `#!python use_query` with a different ORM

    ... then you can either set a custom `#!python postprocessor`, or disable all postprocessing behavior by modifying the `#!python postprocessor=...` parameter. In the example below, we will set the `#!python postprocessor` to `#!python None` to disable postprocessing behavior.

    === "components.py"

        ```python
        {% include "../../examples/python/use_query_postprocessor_disable.py" %}
        ```

    If you wish to create a custom `#!python postprocessor`, you will need to create a function where the first must be the query `#!python data`. All proceeding arguments are optional `#!python postprocessor_kwargs` (see below). This `#!python postprocessor` function must return the modified `#!python data`.

    === "components.py"

        ```python
        {% include "../../examples/python/use_query_postprocessor_change.py" %}
        ```

    ---

    <font size="4">**`#!python postprocessor_kwargs`**</font>

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you have deep nested trees of relational data, this may not be a desirable behavior. In these scenarios, you may prefer to manually fetch these relational fields using a second `#!python use_query` hook.

    You can disable the prefetching behavior of the default `#!python postprocessor` (located at `#!python reactpy_django.utils.django_query_postprocessor`) via the `#!python postprocessor_kwargs=...` parameter.

    === "components.py"

        ```python
        {% include "../../examples/python/use_query_postprocessor_kwargs.py" %}
        ```

    _Note: In Django's ORM design, the field name to access foreign keys is [postfixed with `_set`](https://docs.djangoproject.com/en/stable/topics/db/examples/many_to_one/) by default._

??? question "Can I make ORM calls without hooks?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

??? question "Can I force a query to run again?"

    `#!python use_query` can be re-executed by calling `#!python refetch()` on your `#!python use_query` result.

    The example below uses an `#!python onClick` event to determine when to reset the query.

    === "components.py"

        ```python
        {% include "../../examples/python/use_query_refetch.py" %}
        ```

??? question "Why does the example query function return `#!python TodoItem.objects.all()`?"

    This design decision was based on [Apollo's `#!javascript useQuery` hook](https://www.apollographql.com/docs/react/data/queries/), but ultimately helps avoid Django's `#!python SynchronousOnlyOperation` exceptions.

    With the `#!python Model` or `#!python QuerySet` your function returns, this hook uses the [default postprocessor](./utils.md#django-query-postprocessor) to ensure that all [deferred](https://docs.djangoproject.com/en/stable/ref/models/instances/#django.db.models.Model.get_deferred_fields) or [lazy](https://docs.djangoproject.com/en/stable/topics/db/queries/#querysets-are-lazy) fields are executed.

---

### Use Mutation

Modify data in the background, typically to [create/update/delete](https://www.sumologic.com/glossary/crud/) data from the Django ORM.

Mutation functions can `#!python return False` to manually prevent your `#!python refetch=...` function from executing. All other returns are ignored.

Mutation functions can be sync or async.

=== "components.py"

    ```python
    {% include "../../examples/python/use_mutation.py" %}
    ```

=== "models.py"

    ```python
    {% include "../../examples/python/todo_item_model.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python mutation` | `#!python Callable[FuncParams, bool | None] | Callable[FuncParams, Awaitable[bool | None]]` | A callable that performs Django ORM create, update, or delete functionality. If this function returns `#!python False`, then your `#!python refetch` function will not be used. | N/A |
    | `#!python thread_sensitive` | `#!python bool` | Whether to run the mutation in thread sensitive mode. This setting only applies to sync functions, and is turned on by default due to Django ORM limitations. | `#!python True` |
    | `#!python refetch` | `#!python Callable[..., Any] | Sequence[Callable[..., Any]] | None` | A query function (the function you provide to your `#!python use_query` hook) or a sequence of query functions that need a `#!python refetch` if the mutation succeeds. This is useful for refreshing data after a mutation has been performed. | `#!python None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Mutation[FuncParams]` | An object containing `#!python loading`/`#!python error` states, and a `#!python reset` callable that will set `#!python loading`/`#!python error` states to defaults. This object can be called to run the query. |

??? question "How can I provide arguments to my mutation function?"

    `#!python *args` and `#!python **kwargs` can be provided to your mutation function via `#!python mutation(...)` parameters.

    === "components.py"

        ```python
        {% include "../../examples/python/use_mutation_args_kwargs.py" %}
        ```

??? question "How can I customize this hook's behavior?"

    This hook has several parameters that can be used to customize behavior.

    Below are examples of values that can be modified.

    ---

    <font size="4">**`#!python thread_sensitive`**</font>

    Whether to run your synchronous mutation function in thread sensitive mode. Thread sensitive mode is turned on by default due to Django ORM limitations. See Django's [`sync_to_async` docs](https://docs.djangoproject.com/en/stable/topics/async/#sync-to-async) docs for more information.

    This setting only applies to sync query functions, and will be ignored for async functions.

    === "components.py"

        ```python
        {% include "../../examples/python/use_mutation_thread_sensitive.py" %}
        ```

??? question "Can I make ORM calls without hooks?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

??? question "Can I force a mutation run again?"

    `#!python use_mutation` can be re-executed by calling `#!python reset()` on your `#!python use_mutation` result.

    For example, take a look at `#!python reset_event` below.

    === "components.py"

        ```python
        {% include "../../examples/python/use_mutation_reset.py" %}
        ```

    === "models.py"

        ```python
        {% include "../../examples/python/todo_item_model.py" %}
        ```

??? question "Can `#!python use_mutation` trigger a refetch of `#!python use_query`?"

    `#!python use_mutation` can queue a refetch of a `#!python use_query` via the `#!python refetch=...` argument.

    The example below is a merge of the `#!python use_query` and `#!python use_mutation` examples above with the addition of a `#!python use_mutation(refetch=...)` argument.

    Please note that `#!python refetch` will cause all `#!python use_query` hooks that use `#!python get_items` in the current component tree will be refetched.

    === "components.py"

        ```python
        {% include "../../examples/python/use_mutation_query_refetch.py" %}
        ```

    === "models.py"

        ```python
        {% include "../../examples/python/todo_item_model.py" %}
        ```

---

## User Hooks

---

### Use Auth

Provides a `#!python NamedTuple` containing `#!python async login` and `#!python async logout` functions.

This hook utilizes the Django's authentication framework in a way that provides **persistent** login.

=== "components.py"

    ```python
    {% include "../../examples/python/use_auth.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python UseAuthTuple` | A named tuple containing `#!python login` and `#!python logout` async functions. |

??? warning "Extra Django configuration required"

    Your ReactPy WebSocket must utilize `#!python AuthMiddlewareStack` in order to use this hook.

    {% include "../../includes/auth-middleware-stack.md" %}

??? question "Why use this instead of `#!python channels.auth.login`?"

    The `#!python channels.auth.*` functions cannot trigger re-renders of your ReactPy components. Additionally, they do not provide persistent authentication when used within ReactPy.

    This is a result of Django's authentication design, which requires cookies to retain login status. ReactPy is rendered via WebSockets, and browsers do not allow active WebSocket connections to modify cookies.

    To work around this limitation, when `#!python use_auth().login()` is called within your application, ReactPy performs the following process...

    1. The server authenticates the user into the WebSocket
    2. The server generates a temporary login token
    3. The server commands the browser to use the login token (via HTTP)
    4. The client performs the HTTP request
    5. The server returns the HTTP response, which contains all necessary cookies
    6. The client stores these cookies in the browser

    This ultimately results in persistent authentication which will be retained even if the browser tab is refreshed.

---

### Use User

Shortcut that returns the WebSocket or HTTP connection's `#!python User`.

=== "components.py"

    ```python
    {% include "../../examples/python/use_user.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python AbstractUser` | A Django `#!python User`, which can also be an `#!python AnonymousUser`. |

---

### Use User Data

Store or retrieve a `#!python dict` containing arbitrary data specific to the connection's `#!python User`.

This hook is useful for storing user-specific data, such as preferences or settings.

User data saved with this hook is stored within the `#!python REACTPY_DATABASE`.

=== "components.py"

    ```python
    {% include "../../examples/python/use_user_data.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python default_data` | `#!python None | dict[str, Callable[[], Any] | Callable[[], Awaitable[Any]] | Any]` | A dictionary containing `#!python {key: default_value}` pairs. For computationally intensive defaults, your `#!python default_value` can be sync or async functions that return the value to set. | `#!python None` |
    | `#!python save_default_data` | `#!python bool` | If `#!python True`, `#!python default_data` values will automatically be stored within the database if they do not exist. | `#!python False` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python UserData` | A `#!python NamedTuple` containing a `#!python Query` and `#!python Mutation` objects used to access/modify user data. Read the `#!python use_query` and `#!python use_mutation` docs for more details. |

??? question "How do I set default values?"

    You can configure default user data via the `#!python default_data` parameter.

    This parameter accepts a dictionary containing a `#!python {key: default_value}` pairs. For computationally intensive defaults, your `#!python default_value` can be sync or async functions that return the value to set.

    === "components.py"

        ```python
        {% include "../../examples/python/use_user_data_defaults.py" %}
        ```

---

## Communication Hooks

---

### Use Channel Layer

Subscribe to a [Django Channels Layer](https://channels.readthedocs.io/en/latest/topics/channel_layers.html) to communicate messages.

Layers are a multiprocessing-safe communication system that allows you to send/receive messages between different parts of your application.

This is often used to create chat systems, synchronize data between components, or signal re-renders from outside your components.

=== "components.py"

    ```python
    {% include "../../examples/python/use_channel_layer.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python channel` | `#!python str | None` | The name of the channel this hook will send/receive messages on. If `#!python group` is defined and `#!python channel` is `#!python None`, ReactPy will automatically generate a unique channel name. | `#!python None` |
    | `#!python group` | `#!python str | None` | If configured, the `#!python channel` is added to a `#!python group` and any messages sent by `#!python AsyncMessageSender` is broadcasted to all channels within the `#!python group`. | `#!python None` |
    | `#!python receiver` | `#!python AsyncMessageReceiver | None` | An async function that receives a `#!python message: dict` from a channel. | `#!python None` |
    | `#!python layer` | `#!python str` | The Django Channels layer to use. This layer must be defined in `settings.py:CHANNEL_LAYERS`. | `#!python 'default'` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python AsyncMessageSender` | An async callable that can send messages to the channel(s). This callable accepts a single argument, `#!python message: dict`, which is the data sent to the channel or group of channels. |

??? warning "Extra Django configuration required"

    In order to use this hook, you will need to configure Django to enable channel layers.

    The [Django Channels documentation](https://channels.readthedocs.io/en/latest/topics/channel_layers.html#configuration) has information on what steps you need to take.

    Here is a short summary of the most common installation steps:

    1. Install [`redis`](https://redis.io/download/) on your machine.

    2. Install `channels-redis` in your Python environment.

        ```bash linenums="0"
        pip install channels-redis
        ```

    3. Configure your `settings.py` to use `#!python RedisChannelLayer` as your layer backend.

        ```python linenums="0"
        CHANNEL_LAYERS = {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {
                    "hosts": [("127.0.0.1", 6379)],
                },
            },
        }
        ```

??? tip "Learn about the quirks of Django Channel Layers"

    ReactPy tries to simplify the process of using Django Channels Layers, but it is important to understand how they work.

    There are a few quirks of Django Channels Layers to be aware of:

    - Any given `#!python channel` should only have one `#!python receiver` registered to it, under normal circumstances.
        - This is why ReactPy automatically generates a unique channel name when using `#!python group`.
            - When using `#!python group` within this hook, it is suggested to leave `#!python channel` undefined to let ReactPy automatically create a unique channel name (unless you know what you are doing).
        - If you have multiple receivers for the same `#!python channel`, only one receiver will get the result.
            - This quirk extends to groups as well. For example, If you have two component instances that use the same `#!python channel` within a `#!python group`, the message will only reach one receiver (for that channel).
    - Channels exist independently of their `#!python group`.
        -  Groups are just a loose collection of channel names where a copy of each message can be sent.
        -  As a result, Django allows you to send messages directly to a `#!python channel` even if it is within a `#!python group`.
    - By default, `#!python RedisChannelLayer` will close groups once they have existed for more than 24 hours.
        - You need to create your own subclass of `#!python RedisChannelLayer` to change this behavior.
    - By default, `#!python RedisChannelLayer` only allows 100 messages backlogged within a `#!python channel` receive queue.
        - Rapidly sending messages can overwhelm this queue, resulting in new messages being dropped.
        - If you expect to exceed this limit, you need to create your own subclass of `#!python RedisChannelLayer` to change this behavior.

??? question "How do I broadcast a message to multiple components?"

    Groups allow you to broadcast messages to all channels within that group. If you do not define a `#!python channel` while using groups, ReactPy will automatically generate a unique channel name for you.

    In the example below, since all components use the same channel `#!python group`, messages sent by `#!python my_sender_component` will reach all existing instances of `#!python my_receiver_component_1` and `#!python my_receiver_component_2`.

    === "components.py"

        ```python
        {% include "../../examples/python/use_channel_layer_group.py" %}
        ```

??? question "How do I send a message to a single component (point-to-point communication)?"

    The most common way of using `#!python use_channel_layer` is to broadcast messages to multiple components via a `#!python group`.

    However, you can also use this hook to establish unidirectional, point-to-point communication towards a single `#!python receiver` function. This is slightly more efficient since it avoids the overhead of `#!python group` broadcasting.

    In the example below, `#!python my_sender_component` will communicate directly to a single instance of `#!python my_receiver_component`. This is achieved by defining a `#!python channel` while omitting the `#!python group` parameter.

    === "components.py"

        ```python
        {% include "../../examples/python/use_channel_layer_single.py" %}
        ```

    Note that if you have multiple instances of `#!python my_receiver_component` using the same `#!python channel`, only one will receive the message.

??? question "How do I signal a re-render from something that isn't a component?"

    There are occasions where you may want to signal to the `#!python use_channel_layer` hook from something that isn't a component, such as a Django [model signal](https://docs.djangoproject.com/en/stable/topics/signals/).

    In these cases, you can use the `#!python use_channel_layer` hook to receive a signal within your component, and then use the `#!python get_channel_layer().send(...)` to send the signal.

    In the example below, the sender will signal every time `#!python ExampleModel` is saved. Then, when the receiver gets this signal, it explicitly calls `#!python set_message(...)` to trigger a re-render.

    === "signals.py"

        ```python
        {% include "../../examples/python/use_channel_layer_signal_sender.py" %}
        ```

    === "components.py"

        ```python
        {% include "../../examples/python/use_channel_layer_signal_receiver.py" %}
        ```

---

## Connection Hooks

---

### Use Connection

Returns the active connection, which is either a Django [WebSocket](https://channels.readthedocs.io/en/stable/topics/consumers.html#asyncjsonwebsocketconsumer) or a [HTTP Request](https://docs.djangoproject.com/en/stable/ref/request-response/#django.http.HttpRequest).

=== "components.py"

    ```python
    {% include "../../examples/python/use_connection.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Connection` | An object that contains a `carrier` (`WebSocket` or `HttpRequest`), `scope`, and `location`. |

---

### Use Scope

Shortcut that returns the WebSocket or HTTP connection's [scope](https://channels.readthedocs.io/en/stable/topics/consumers.html#scope).

=== "components.py"

    ```python
    {% include "../../examples/python/use_scope.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python MutableMapping[str, Any]` | The connection's `#!python scope`. |

---

### Use Location

Shortcut that returns the browser's current `#!python Location`.

=== "components.py"

    ```python
    {% include "../../examples/python/use_location.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Location` | An object containing the current URL's `#!python pathname` and `#!python search` query. |

---

### Use Origin

Shortcut that returns the WebSocket or HTTP connection's `#!python origin`.

You can expect this hook to provide strings such as `http://example.com`.

=== "components.py"

    ```python
    {% include "../../examples/python/use_origin.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python str | None` | A string containing the browser's current origin, obtained from WebSocket or HTTP headers (if available). |

---

### Use Root ID

Shortcut that returns the root component's `#!python id` from the WebSocket or HTTP connection.

The root ID is a randomly generated `#!python uuid4`. It is notable to mention that it is persistent across the current connection. The `uuid` is reset only when the page is refreshed.

This is useful when used in combination with [`#!python use_channel_layer`](#use-channel-layer) to send messages to a specific component instance.

=== "components.py"

    ```python
    {% include "../../examples/python/use_root_id.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python str` | A string containing the root component's `#!python id`. |

---

### Use Re-render

Returns a function that can be used to trigger a re-render of the entire component tree.

=== "components.py"

    ```python
    {% include "../../examples/python/use_rerender.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `#!python None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Callable[[], None]` | A function that triggers a re-render of the entire component tree. |
