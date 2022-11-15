???+ summary

    Prefabricated hooks can be used within your `components.py` to help simplify development.

??? tip "Looking for standard ReactJS hooks?"

    Standard ReactJS hooks are contained within [`idom-team/idom`](https://github.com/idom-team/idom). Since `idom` is installed by default alongside `django-idom`, you can import them at any time.

    Check out the [IDOM Core docs](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html#basic-hooks) to see what hooks are available!

## Use Query

The `use_query` hook is used fetch Django ORM queries.

The function you provide into this hook must return either a `Model` or `QuerySet`.

=== "components.py"

    ```python linenums="1"
    from example_project.my_app.models import TodoItem
    from idom import component, html
    from django_idom.hooks import use_query

    def get_items():
        return TodoItem.objects.all()

    @component
    def todo_list():
        item_query = use_query(get_items)

        if item_query.loading:
            rendered_items = html.h2("Loading...")
        elif item_query.error:
            rendered_items = html.h2("Error when loading!")
        else:
            rendered_items = html.ul(html.li(item, key=item) for item in item_query.data)

        return rendered_items
    ```

=== "models.py"

    ```python linenums="1"
    from django.db import models

    class TodoItem(models.Model):
        text = models.CharField(max_length=255)
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `query` | `Callable[_Params, _Result | None]` | A callable that returns a Django `Model` or `QuerySet`. | N/A |
    | `*args` | `_Params.args` | Positional arguments to pass into `query`. | N/A |
    | `**kwargs` | `_Params.kwargs` | Keyword arguments to pass into `query`. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Query[_Result | None]` | An object containing `loading`/`error` states, your `data` (if the query has successfully executed), and a `refetch` callable that can be used to re-run the query. |

??? question "Can I make ORM calls without hooks?"

    Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

    This may be resolved in a future version of Django containing an asynchronous ORM.

??? question "Why does the example `get_items` function return a `Model` or `QuerySet`?"

    This was a technical design decision to [based on Apollo](https://www.apollographql.com/docs/react/data/mutations/#usemutation-api), but ultimately helps avoid Django's `SynchronousOnlyOperation` exceptions.

    The `use_query` hook ensures the provided `Model` or `QuerySet` executes all [deferred](https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.get_deferred_fields)/[lazy queries](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy) safely prior to reaching your components.

??? question "What is an "ORM"?"

    A Python **Object Relational Mapper** is an API for your code to access a database.

    See the [Django ORM documentation](https://docs.djangoproject.com/en/dev/topics/db/queries/) for more information.

## Use Mutation

The `use_mutation` hook is used to create, update, or delete Django ORM objects.

The function you provide into this hook will have no return value.

=== "components.py"

    ```python linenums="1"
    from example_project.my_app.models import TodoItem
    from idom import component, html
    from django_idom.hooks import use_mutation

    def add_item(text: str):
        TodoItem(text=text).save()

    @component
    def todo_list():
        def submit_event(event):
            if event["key"] == "Enter":
                item_mutation.execute(text=event["target"]["value"])

        item_mutation = use_mutation(add_item)
        if item_mutation.loading:
            mutation_status = html.h2("Adding...")
        elif item_mutation.error:
            mutation_status = html.h2("Error when adding!")
        else:
            mutation_status = ""

        return html.div(
            html.label("Add an item:"),
            html.input({"type": "text", "onKeyDown": submit_event}),
            mutation_status,
        )
    ```

=== "models.py"

    {% include-markdown "../../includes/examples.md" start="<!--todo-model-start-->" end="<!--todo-model-end-->" %}

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

??? question "Can `use_mutation` trigger a refetch of `use_query`?"

    Yes, `use_mutation` can queue a refetch of a `use_query` via the `refetch=...` argument.

    The example below is a merge of the `use_query` and `use_mutation` examples above with the addition of a `refetch` argument on `use_mutation`.

    Please note that any `use_query` hooks that use `get_items` will be refetched upon a successful mutation.

    === "components.py"

        ```python linenums="1"
        from example_project.my_app.models import TodoItem
        from idom import component, html
        from django_idom.hooks import use_mutation

        def get_items():
            return TodoItem.objects.all()

        def add_item(text: str):
            TodoItem(text=text).save()

        @component
        def todo_list():
            def submit_event(event):
                if event["key"] == "Enter":
                    item_mutation.execute(text=event["target"]["value"])

            item_query = use_query(get_items)
            if item_query.loading:
                rendered_items = html.h2("Loading...")
            elif item_query.error:
                rendered_items = html.h2("Error when loading!")
            else:
                rendered_items = html.ul(html.li(item, key=item) for item in item_query.data)

            item_mutation = use_mutation(add_item, refetch=get_items)
            if item_mutation.loading:
                mutation_status = html.h2("Adding...")
            elif item_mutation.error:
                mutation_status = html.h2("Error when adding!")
            else:
                mutation_status = ""

            return html.div(
                html.label("Add an item:"),
                html.input({"type": "text", "onKeyDown": submit_event}),
                mutation_status,
                rendered_items,
            )
        ```

    === "models.py"

        {% include-markdown "../../includes/examples.md" start="<!--todo-model-start-->" end="<!--todo-model-end-->" %}

??? question "Can I make a failed `use_mutation` try again?"

    Yes, a `use_mutation` can be re-performed by calling `reset()` on your `use_mutation` instance.

    For example, take a look at `reset_event` below.

    === "components.py"

        ```python linenums="1"
        from example_project.my_app.models import TodoItem
        from idom import component, html
        from django_idom.hooks import use_mutation

        def add_item(text: str):
            TodoItem(text=text).save()

        @component
        def todo_list():
            def reset_event(event):
                item_mutation.reset()

            def submit_event(event):
                if event["key"] == "Enter":
                    item_mutation.execute(text=event["target"]["value"])

            item_mutation = use_mutation(add_item)
            if item_mutation.loading:
                mutation_status = html.h2("Adding...")
            elif item_mutation.error:
                mutation_status = html.button({"onClick": reset_event}, "Error: Try again!")
            else:
                mutation_status = ""

            return html.div(
                html.label("Add an item:"),
                html.input({"type": "text", "onKeyDown": submit_event}),
                mutation_status,
            )
        ```

    === "models.py"

        {% include-markdown "../../includes/examples.md" start="<!--todo-model-start-->" end="<!--todo-model-end-->" %}

??? question "Can I make ORM calls without hooks?"

    Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

    This may be resolved in a future version of Django containing an asynchronous ORM.

    However, even when resolved it is best practice to perform ORM queries within the `use_query` in order to handle `loading` and `error` states.

??? question "What is an "ORM"?"

    A Python **Object Relational Mapper** is an API for your code to access a database.

    See the [Django ORM documentation](https://docs.djangoproject.com/en/dev/topics/db/queries/) for more information.

## Use Websocket

You can fetch the Django Channels [websocket](https://channels.readthedocs.io/en/stable/topics/consumers.html#asyncjsonwebsocketconsumer) at any time by using `use_websocket`.

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.hooks import use_websocket

    @component
    def my_component():
        my_websocket = use_websocket()
        return html.div(my_websocket)
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `IdomWebsocket` | The component's websocket. |

## Use Scope

This is a shortcut that returns the Websocket's [`scope`](https://channels.readthedocs.io/en/stable/topics/consumers.html#scope).

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.hooks import use_scope

    @component
    def my_component():
        my_scope = use_scope()
        return html.div(my_scope)
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `dict[str, Any]` | The websocket's `scope`. |

## Use Location

This is a shortcut that returns the Websocket's `path`.

You can expect this hook to provide strings such as `/idom/my_path`.

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.hooks import use_location

    @component
    def my_component():
        my_location = use_location()
        return html.div(my_location)
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Location` | A object containing the current URL's `pathname` and `search` query. |

??? info "This hook's behavior will be changed in a future update"

    This hook will be updated to return the browser's currently active path. This change will come in alongside IDOM URL routing support.

    Check out [idom-team/idom-router#2](https://github.com/idom-team/idom-router/issues/2) for more information.

## Use Origin

This is a shortcut that returns the Websocket's `origin`.

You can expect this hook to provide strings such as `http://example.com`.

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.hooks import use_origin

    @component
    def my_component():
        my_origin = use_origin()
        return html.div(my_origin)
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    `None`

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `str | None` | A string containing the browser's current origin, obtained from websocket headers (if available). |
