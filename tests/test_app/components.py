import inspect

from django.http import HttpRequest
from django.shortcuts import render
from idom import component, hooks, html, web
from test_app.models import TodoItem

import django_idom
from django_idom.components import view_to_component
from django_idom.hooks import use_mutation, use_query

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
def use_origin():
    origin = django_idom.hooks.use_origin()
    success = bool(origin)
    return html.div(
        {"id": "use-origin", "data-success": success},
        f"use_origin: {origin}",
        html.hr(),
    )


@component
def django_css():
    return html.div(
        {"id": "django-css"},
        django_idom.components.django_css("django-css-test.css", key="test"),
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
            django_idom.components.django_js("django-js-test.js", key="test"),
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


def get_items_query():
    return TodoItem.objects.all()


def add_item_mutation(text: str):
    existing = TodoItem.objects.filter(text=text).first()
    if existing:
        if existing.done:
            existing.done = False
            existing.save()
        else:
            return False
    else:
        TodoItem(text=text, done=False).save()


def toggle_item_mutation(item: TodoItem):
    item.done = not item.done
    item.save()


@component
def todo_list():
    input_value, set_input_value = hooks.use_state("")
    items = use_query(get_items_query)
    toggle_item = use_mutation(toggle_item_mutation)

    if items.error:
        rendered_items = html.h2(f"Error when loading - {items.error}")
    elif items.data is None:
        rendered_items = html.h2("Loading...")
    else:
        rendered_items = html._(
            html.h3("Not Done"),
            _render_items([i for i in items.data if not i.done], toggle_item),
            html.h3("Done"),
            _render_items([i for i in items.data if i.done], toggle_item),
        )

    add_item = use_mutation(add_item_mutation, refetch=get_items_query)

    if add_item.loading:
        mutation_status = html.h2("Working...")
    elif add_item.error:
        mutation_status = html.h2(f"Error when adding - {add_item.error}")
    else:
        mutation_status = ""  # type: ignore

    def on_submit(event):
        if event["key"] == "Enter":
            add_item.execute(text=event["target"]["value"])
            set_input_value("")

    def on_change(event):
        set_input_value(event["target"]["value"])

    return html.div(
        html.label("Add an item:"),
        html.input(
            {
                "type": "text",
                "id": "todo-input",
                "value": input_value,
                "onKeyPress": on_submit,
                "onChange": on_change,
            }
        ),
        mutation_status,
        rendered_items,
        html.hr(),
    )


def _render_items(items, toggle_item):
    return html.ul(
        [
            html.li(
                {"id": f"todo-item-{item.text}"},
                item.text,
                html.input(
                    {
                        "id": f"todo-item-{item.text}-checkbox",
                        "type": "checkbox",
                        "checked": item.done,
                        "onChange": lambda event, i=item: toggle_item.execute(i),
                    }
                ),
                key=item.text,
            )
            for item in items
        ]
    )


view_to_component_sync_func = view_to_component(views.view_to_component_sync_func)
view_to_component_async_func = view_to_component(views.view_to_component_async_func)
view_to_component_sync_class = view_to_component(views.ViewToComponentSyncClass)
view_to_component_async_class = view_to_component(views.ViewToComponentAsyncClass)
view_to_component_template_view_class = view_to_component(
    views.ViewToComponentTemplateViewClass
)
_view_to_component_sync_func_compatibility = view_to_component(
    views.view_to_component_sync_func_compatibility, compatibility=True
)
_view_to_component_async_func_compatibility = view_to_component(
    views.view_to_component_async_func_compatibility, compatibility=True
)
_view_to_component_sync_class_compatibility = view_to_component(
    views.ViewToComponentSyncClassCompatibility, compatibility=True
)
_view_to_component_async_class_compatibility = view_to_component(
    views.ViewToComponentAsyncClassCompatibility, compatibility=True
)
_view_to_component_template_view_class_compatibility = view_to_component(
    views.ViewToComponentTemplateViewClassCompatibility, compatibility=True
)
view_to_component_script = view_to_component(views.view_to_component_script)
_view_to_component_request = view_to_component(views.view_to_component_request)
_view_to_component_args = view_to_component(views.view_to_component_args)
_view_to_component_kwargs = view_to_component(views.view_to_component_kwargs)


@component
def view_to_component_sync_func_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_sync_func_compatibility(key="test"),
        html.hr(),
    )


@component
def view_to_component_async_func_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_async_func_compatibility(),
        html.hr(),
    )


@component
def view_to_component_sync_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_sync_class_compatibility(),
        html.hr(),
    )


@component
def view_to_component_async_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_async_class_compatibility(),
        html.hr(),
    )


@component
def view_to_component_template_view_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_template_view_class_compatibility(),
        html.hr(),
    )


@component
def view_to_component_request():
    request, set_request = hooks.use_state(None)

    def on_click(_):
        post_request = HttpRequest()
        post_request.method = "POST"
        set_request(post_request)  # type: ignore

    return html._(
        html.button(
            {"id": f"{inspect.currentframe().f_code.co_name}_btn", "onClick": on_click},  # type: ignore
            "Click me",
        ),
        _view_to_component_request(request=request),
    )


@component
def view_to_component_args():
    success, set_success = hooks.use_state("false")

    def on_click(_):
        set_success("")

    return html._(
        html.button(
            {"id": f"{inspect.currentframe().f_code.co_name}_btn", "onClick": on_click},  # type: ignore
            "Click me",
        ),
        _view_to_component_args(None, success),
    )


@component
def view_to_component_kwargs():
    success, set_success = hooks.use_state("false")

    def on_click(_):
        set_success("")

    return html._(
        html.button(
            {"id": f"{inspect.currentframe().f_code.co_name}_btn", "onClick": on_click},  # type: ignore
            "Click me",
        ),
        _view_to_component_kwargs(success=success),
    )


@view_to_component
def view_to_component_decorator(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},  # type: ignore
    )


@view_to_component(strict_parsing=False)
def view_to_component_decorator_args(request):
    return render(
        request,
        "view_to_component.html",
        {"test_name": inspect.currentframe().f_code.co_name},  # type: ignore
    )
