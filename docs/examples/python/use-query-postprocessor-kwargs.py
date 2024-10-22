from example.models import TodoItem
from reactpy import component
from reactpy_django.hooks import use_query


def get_model_with_relationships():
    """This is an example query function that gets `MyModel` which has a ManyToMany field, and
    additionally other models that have formed a ForeignKey association to `MyModel`.

    ManyToMany Field: `many_to_many_field`
    ForeignKey Field: `foreign_key_field_set`
    """
    return TodoItem.objects.get(id=1)


@component
def my_component():
    query = use_query(
        get_model_with_relationships,
        postprocessor_kwargs={"many_to_many": False, "many_to_one": False},
    )

    if query.loading or query.error or not query.data:
        return None

    # By disabling `many_to_many` and `many_to_one`, accessing these fields will now
    # generate a `SynchronousOnlyOperation` exception
    return f"{query.data.many_to_many_field} {query.data.foriegn_key_field_set}"
