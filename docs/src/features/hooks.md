???+ summary

    Prefabricated hooks can be used within your `components.py` to help simplify development.

??? tip "Looking for standard ReactJS hooks?"

    Standard ReactJS hooks are contained within [`idom-team/idom`](https://github.com/idom-team/idom). Since `idom` is installed by default alongside `django-idom`, you can import them at any time.

    Check out the [IDOM Core docs](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html#basic-hooks) to see what hooks are available!

## Use Query

The `use_query` hook is used fetch Django ORM queries.

The function you provide into this hook must return either a `Model` or `QuerySet`.

=== "components.py"

    ```python
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

    ```python
    from django.db import models

    class TodoItem(models.Model):
        text = models.CharField(max_length=255)
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
        from idom import component
        from django_idom.hooks import use_query

        def example_query(value: int, other_value: bool = False):
            ...

        @component
        def my_component():
            query = use_query(
                example_query,
                123,
                other_value=True,
            )

            ...
        ```

??? question "Why does the example `get_items` function return `TodoItem.objects.all()`?"

    This was a technical design decision to based on [Apollo's `useQuery` hook](https://www.apollographql.com/docs/react/data/queries/), but ultimately helps avoid Django's `SynchronousOnlyOperation` exceptions.

    The `use_query` hook ensures the provided `Model` or `QuerySet` executes all [deferred](https://docs.djangoproject.com/en/dev/ref/models/instances/#django.db.models.Model.get_deferred_fields)/[lazy queries](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy) safely prior to reaching your components.

??? question "Can this hook be used for things other than the Django ORM?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you...

    1. Want to use this hook to defer IO intensive tasks to be computed in the background
    2. Want to to utilize `use_query` with a different ORM

    ... then you can disable all postprocessing behavior by modifying the `QueryOptions.postprocessor` parameter. In the example below, we will set the `postprocessor` to `None` to disable postprocessing behavior.

    === "components.py"

        ```python
        from idom import component
        from django_idom.types import QueryOptions
        from django_idom.hooks import use_query

        def execute_io_intensive_operation():
            """This is an example query function that does something IO intensive."""
            pass

        @component
        def todo_list():
            query = use_query(
                QueryOptions(postprocessor=None),
                execute_io_intensive_operation,
            )

            if query.loading or query.error:
                return None

            return str(query.data)
        ```

    If you wish to create a custom `postprocessor`, you will need to create a callable.

    The first argument of `postprocessor` must be the query `data`. All proceeding arguments
    are optional `postprocessor_kwargs` (see below). This `postprocessor` must return
    the modified `data`.

    === "components.py"

        ```python
        from idom import component
        from django_idom.types import QueryOptions
        from django_idom.hooks import use_query

        def my_postprocessor(data, example_kwarg=True):
            if example_kwarg:
                return data

            return dict(data)

        def execute_io_intensive_operation():
            """This is an example query function that does something IO intensive."""
            pass

        @component
        def todo_list():
            query = use_query(
                QueryOptions(
                    postprocessor=my_postprocessor,
                    postprocessor_kwargs={"example_kwarg": False},
                ),
                execute_io_intensive_operation,
            )

            if query.loading or query.error:
                return None

            return str(query.data)
        ```

??? question "How can I prevent this hook from recursively fetching `ManyToMany` fields or `ForeignKey` relationships?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-fetch-start-->" end="<!--orm-fetch-end-->" %}

    However, if you have deep nested trees of relational data, this may not be a desirable behavior. In these scenarios, you may prefer to manually fetch these relational fields using a second `use_query` hook.

    You can disable the prefetching behavior of the default `postprocessor` (located at `django_idom.utils.django_query_postprocessor`) via the `QueryOptions.postprocessor_kwargs` parameter.

    === "components.py"

        ```python
        from example_project.my_app.models import MyModel
        from idom import component
        from django_idom.types import QueryOptions
        from django_idom.hooks import use_query

        def get_model_with_relationships():
            """This is an example query function that gets `MyModel` which has a ManyToMany field, and
            additionally other models that have formed a ForeignKey association to `MyModel`.

            ManyToMany Field: `many_to_many_field`
            ForeignKey Field: `foreign_key_field_set`
            """
            return MyModel.objects.get(id=1)

        @component
        def todo_list():
            query = use_query(
                QueryOptions(postprocessor_kwargs={"many_to_many": False, "many_to_one": False}),
                get_model_with_relationships,
            )

            if query.loading or query.error:
                return None

            # By disabling `many_to_many` and `many_to_one`, accessing these fields will now
            # generate a `SynchronousOnlyOperation` exception
            return f"{query.data.many_to_many_field} {query.data.foriegn_key_field_set}"
        ```

    _Note: In Django's ORM design, the field name to access foreign keys is [always be postfixed with `_set`](https://docs.djangoproject.com/en/dev/topics/db/examples/many_to_one/)._

??? question "Can I make ORM calls without hooks?"

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

## Use Mutation

The `use_mutation` hook is used to create, update, or delete Django ORM objects.

The function you provide into this hook will have no return value.

=== "components.py"

    ```python
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

??? question "How can I provide arguments to my mutation function?"

    `*args` and `**kwargs` can be provided to your mutation function via `mutation.execute` parameters.

    === "components.py"

        ```python
        from idom import component
        from django_idom.hooks import use_mutation

        def example_mutation(value: int, other_value: bool = False):
            ...

        @component
        def my_component():
            mutation = use_mutation(example_mutation)

            mutation.execute(123, other_value=True)

            ...
        ```

??? question "Can `use_mutation` trigger a refetch of `use_query`?"

    Yes, `use_mutation` can queue a refetch of a `use_query` via the `refetch=...` argument.

    The example below is a merge of the `use_query` and `use_mutation` examples above with the addition of a `refetch` argument on `use_mutation`.

    Please note that any `use_query` hooks that use `get_items` will be refetched upon a successful mutation.

    === "components.py"

        ```python
        from example_project.my_app.models import TodoItem
        from idom import component, html
        from django_idom.hooks import use_mutation

        def get_items():
            return TodoItem.objects.all()

        def add_item(text: str):
            TodoItem(text=text).save()

        @component
        def todo_list():
            item_query = use_query(get_items)
            item_mutation = use_mutation(add_item, refetch=get_items)

            def submit_event(event):
                if event["key"] == "Enter":
                    item_mutation.execute(text=event["target"]["value"])

            # Handle all possible query states
            if item_query.loading:
                rendered_items = html.h2("Loading...")
            elif item_query.error:
                rendered_items = html.h2("Error when loading!")
            else:
                rendered_items = html.ul(html.li(item, key=item) for item in item_query.data)

            # Handle all possible mutation states
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

        ```python
        from example_project.my_app.models import TodoItem
        from idom import component, html
        from django_idom.hooks import use_mutation

        def add_item(text: str):
            TodoItem(text=text).save()

        @component
        def todo_list():
            item_mutation = use_mutation(add_item)

            def reset_event(event):
                item_mutation.reset()

            def submit_event(event):
                if event["key"] == "Enter":
                    item_mutation.execute(text=event["target"]["value"])

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

    {% include-markdown "../../includes/orm.md" start="<!--orm-excp-start-->" end="<!--orm-excp-end-->" %}

## Use Websocket

You can fetch the Django Channels [websocket](https://channels.readthedocs.io/en/stable/topics/consumers.html#asyncjsonwebsocketconsumer) at any time by using `use_websocket`.

=== "components.py"

    ```python
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

    ```python
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

    ```python
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

    ```python
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
