from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from reactpy_django.components import view_to_component


@view_to_component(compatibility=True)
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")  # type: ignore[union-attr]
class ExampleView(TemplateView):
    ...
