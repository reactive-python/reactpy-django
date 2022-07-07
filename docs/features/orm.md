??? info "Our suggested ORM access method will be changed in a future update"

    The Django IDOM team is currently assessing the optimal way to integrate the [Django ORM](https://docs.djangoproject.com/en/dev/topics/db/queries/) with our React-style framework.

    This docs page exists to demonstrate how the ORM should be used with the current version of Django IDOM.

    Check out [idom-team/django-idom#79](https://github.com/idom-team/django-idom/issues/79) for more information.

This is the suggested method of using the Django ORM with your components.

```python title="components.py"
from channels.db import database_sync_to_async
from example_project.my_app.models import Category
from idom import component, hooks, html


@component
def simple_list():
    categories, set_categories = hooks.use_state(None)

    @hooks.use_effect
    @database_sync_to_async
    def get_categories():
        if categories:
            return
        set_categories(list(Category.objects.all()))

    if not categories:
        return html.h2("Loading...")

    return html.ul(
        [html.li(category.name, key=category.name) for category in categories]
    )
```

??? question "Why does this example use `list()` within `set_categories`?"

    [Django's ORM is lazy](https://docs.djangoproject.com/en/dev/topics/db/queries/#querysets-are-lazy). Thus, `list()` is used to ensure that the database query is executed while within the hook.

    Failure to do this will result in `SynchronousOnlyOperation` when attempting to access your data.

??? question "Why can't I make ORM calls without hooks?"

    Due to Django's ORM design, database queries must be deferred using hooks. Otherwise, you will see a `SynchronousOnlyOperation` exception.

    This may be resolved in a future version of Django with a natively asynchronous ORM.

??? question "What is an "ORM"?"

    A Python **Object Relational Mapper** is an API for your code to access a database.

    See the [Django ORM documentation](https://docs.djangoproject.com/en/dev/topics/db/queries/) for more information.
