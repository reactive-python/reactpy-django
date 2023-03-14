from django.contrib.auth.decorators import user_passes_test

from reactpy_django.components import view_to_component


@view_to_component(compatibility=True)
@user_passes_test(lambda u: u.is_superuser)  # type: ignore[union-attr]
def example_view(request):
    ...
