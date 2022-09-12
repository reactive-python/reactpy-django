import inspect

from idom import component, hooks, html, web

import django_idom
from django_idom.components import view_to_component

from . import views


@component
def hello_world():
    return html._(html.h1({"id": "hello-world"}, "Hello World!"), html.hr())


@component
def button():
    count, set_count = hooks.use_state(0)
    return html._(
        html.div(
            html.button(
                {"id": "counter-inc", "onClick": lambda event: set_count(count + 1)},
                "Click me!",
            ),
            html.p(
                {"id": "counter-num", "data-count": count},
                f"Current count is: {count}",
            ),
        ),
        html.hr(),
    )


@component
def parameterized_component(x, y):
    total = x + y
    return html._(
        html.h1({"id": "parametrized-component", "data-value": total}, total),
        html.hr(),
    )


victory = web.module_from_template("react", "victory-bar", fallback="...")
VictoryBar = web.export(victory, "VictoryBar")


@component
def simple_bar_chart():
    return html._(VictoryBar(), html.hr())


@component
def use_websocket():
    ws = django_idom.hooks.use_websocket()
    success = bool(ws.scope and ws.close and ws.disconnect and ws.view_id)
    return html.div(
        {"id": "use-websocket", "data-success": success},
        html.hr(),
        f"use_websocket: {ws}",
        html.hr(),
    )


@component
def use_scope():
    scope = django_idom.hooks.use_scope()
    success = len(scope) >= 10 and scope["type"] == "websocket"
    return html.div(
        {"id": "use-scope", "data-success": success},
        f"use_scope: {scope}",
        html.hr(),
    )


@component
def use_location():
    location = django_idom.hooks.use_location()
    success = bool(location)
    return html.div(
        {"id": "use-location", "data-success": success},
        f"use_location: {location}",
        html.hr(),
    )


@component
def django_css():
    return html.div(
        {"id": "django-css"},
        django_idom.components.django_css("django-css-test.css"),
        html.div({"style": {"display": "inline"}}, "django_css: "),
        html.button("This text should be blue."),
        html.hr(),
    )


@component
def django_js():
    success = False
    return html._(
        html.div(
            {"id": "django-js", "data-success": success},
            f"django_js: {success}",
            django_idom.components.django_js("django-js-test.js"),
        ),
        html.hr(),
    )


@component
@django_idom.decorators.auth_required(
    fallback=html.div(
        {"id": "unauthorized-user-fallback"},
        "unauthorized_user: Success",
        html.hr(),
    )
)
def unauthorized_user():
    return html.div(
        {"id": "unauthorized-user"},
        "unauthorized_user: Fail",
        html.hr(),
    )


@component
@django_idom.decorators.auth_required(
    auth_attribute="is_anonymous",
    fallback=html.div(
        {"id": "authorized-user-fallback"},
        "authorized_user: Fail",
        html.hr(),
    ),
)
def authorized_user():
    return html.div(
        {"id": "authorized-user"},
        "authorized_user: Success",
        html.hr(),
    )


@component
def view_to_component_sync_func():
    return view_to_component(views.view_to_component_sync_func)


@component
def view_to_component_async_func():
    return view_to_component(views.view_to_component_async_func)


@component
def view_to_component_sync_class():
    return view_to_component(views.ViewToComponentSyncClass)


@component
def view_to_component_async_class():
    return view_to_component(views.ViewToComponentAsyncClass)


@component
def view_to_component_template_view_class():
    return view_to_component(views.ViewToComponentTemplateViewClass)


@component
def view_to_component_sync_func_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        view_to_component(
            views.view_to_component_sync_func_compatibility, compatibility=True
        ),
        html.hr(),
    )


@component
def view_to_component_async_func_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        view_to_component(
            views.view_to_component_async_func_compatibility, compatibility=True
        ),
        html.hr(),
    )


@component
def view_to_component_sync_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        view_to_component(
            views.ViewToComponentSyncClassCompatibility, compatibility=True
        ),
        html.hr(),
    )


@component
def view_to_component_async_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        view_to_component(
            views.ViewToComponentAsyncClassCompatibility, compatibility=True
        ),
        html.hr(),
    )


@component
def view_to_component_template_view_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        view_to_component(
            views.ViewToComponentTemplateViewClassCompatibility, compatibility=True
        ),
        html.hr(),
    )


@component
def view_to_component_script():
    return view_to_component(views.view_to_component_script)
