import asyncio
import inspect
from pathlib import Path

from channels.db import database_sync_to_async
from django.http import HttpRequest
from django.shortcuts import render
from idom import component, hooks, html, web
from test_app.models import (
    AsyncForiegnChild,
    AsyncRelationalChild,
    AsyncRelationalParent,
    AsyncTodoItem,
    ForiegnChild,
    RelationalChild,
    RelationalParent,
    TodoItem,
)

import django_idom
from django_idom.components import view_to_component

from . import views
from .types import TestObject


@component
def hello_world():
    return html._(html.div({"id": "hello-world"}, "Hello World!"), html.hr())


@component
def button():
    count, set_count = hooks.use_state(0)
    return html._(
        html.div(
            "button:",
            html.button(
                {"id": "counter-inc", "on_click": lambda event: set_count(count + 1)},
                "Click me!",
            ),
            html.p(
                {"id": "counter-num", "data-count": count}, f"Current count is: {count}"
            ),
        ),
        html.hr(),
    )


@component
def parameterized_component(x, y):
    total = x + y
    return html._(
        html.div(
            {"id": "parametrized-component", "data-value": total},
            f"parameterized_component: {total}",
        ),
        html.hr(),
    )


@component
def object_in_templatetag(my_object: TestObject):
    success = bool(my_object and my_object.value)
    co_name = inspect.currentframe().f_code.co_name  # type: ignore
    return html._(
        html.div(
            {"id": co_name, "data-success": success}, f"{co_name}: ", str(my_object)
        ),
        html.hr(),
    )


SimpleButtonModule = web.module_from_file(
    "SimpleButton",
    Path(__file__).parent / "tests" / "js" / "simple-button.js",
    resolve_exports=False,
    fallback="...",
)
SimpleButton = web.export(SimpleButtonModule, "SimpleButton")


@component
def simple_button():
    return html._(
        "simple_button:",
        SimpleButton({"id": "simple-button"}),
        html.hr(),
    )


@component
def use_connection():
    ws = django_idom.hooks.use_connection()
    success = bool(
        ws.scope
        and getattr(ws, "location", None)
        and getattr(ws.carrier, "close", None)
        and getattr(ws.carrier, "disconnect", None)
        and getattr(ws.carrier, "dotted_path", None)
    )
    return html.div(
        {"id": "use-connection", "data-success": success},
        f"use_connection: {ws}",
        html.hr(),
    )


@component
def use_scope():
    scope = django_idom.hooks.use_scope()
    success = len(scope) >= 10 and scope["type"] == "websocket"
    return html.div(
        {"id": "use-scope", "data-success": success}, f"use_scope: {scope}", html.hr()
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


def create_relational_parent() -> RelationalParent:
    child_1 = RelationalChild.objects.create(text="ManyToMany Child 1")
    child_2 = RelationalChild.objects.create(text="ManyToMany Child 2")
    child_3 = RelationalChild.objects.create(text="ManyToMany Child 3")
    child_4 = RelationalChild.objects.create(text="OneToOne Child")
    parent = RelationalParent.objects.create(one_to_one=child_4)
    parent.many_to_many.set((child_1, child_2, child_3))
    parent.save()
    return parent


def get_relational_parent_query():
    return RelationalParent.objects.first() or create_relational_parent()


def get_foriegn_child_query():
    child = ForiegnChild.objects.first()
    if not child:
        child = ForiegnChild.objects.create(
            parent=get_relational_parent_query(), text="Foriegn Child"
        )
        child.save()
    return child


@component
def relational_query():
    foriegn_child = django_idom.hooks.use_query(get_foriegn_child_query)
    relational_parent = django_idom.hooks.use_query(get_relational_parent_query)

    if not relational_parent.data or not foriegn_child.data:
        return

    mtm = relational_parent.data.many_to_many.all()
    oto = relational_parent.data.one_to_one
    mto = relational_parent.data.many_to_one.all()
    fk = foriegn_child.data.parent

    return html.div(
        {
            "id": "relational-query",
            "data-success": bool(mtm) and bool(oto) and bool(mto) and bool(fk),
        },
        html.p(inspect.currentframe().f_code.co_name),
        html.div(f"Relational Parent Many To Many: {mtm}"),
        html.div(f"Relational Parent One To One: {oto}"),
        html.div(f"Relational Parent Many to One: {mto}"),
        html.div(f"Relational Child Foreign Key: {fk}"),
        html.hr(),
    )


async def async_get_or_create_relational_parent():
    parent = await AsyncRelationalParent.objects.afirst()
    if parent:
        return parent

    child_1 = await AsyncRelationalChild.objects.acreate(text="ManyToMany Child 1")
    child_2 = await AsyncRelationalChild.objects.acreate(text="ManyToMany Child 2")
    child_3 = await AsyncRelationalChild.objects.acreate(text="ManyToMany Child 3")
    child_4 = await AsyncRelationalChild.objects.acreate(text="OneToOne Child")
    parent = await AsyncRelationalParent.objects.acreate(one_to_one=child_4)
    await database_sync_to_async(parent.many_to_many.set, thread_sensitive=False)(
        (child_1, child_2, child_3)
    )
    database_sync_to_async(parent.save, thread_sensitive=False)()
    return parent


async def async_get_relational_parent_query():
    # Sleep to avoid race conditions in the test
    await asyncio.sleep(1)
    return await async_get_or_create_relational_parent()


async def async_get_foriegn_child_query():
    child = await AsyncForiegnChild.objects.afirst()
    if not child:
        child = await AsyncForiegnChild.objects.acreate(
            parent=await async_get_or_create_relational_parent(), text="Foriegn Child"
        )
        await database_sync_to_async(child.save, thread_sensitive=False)()
    return child


@component
def async_relational_query():
    foriegn_child = django_idom.hooks.use_query(async_get_foriegn_child_query)
    relational_parent = django_idom.hooks.use_query(async_get_relational_parent_query)

    if not relational_parent.data or not foriegn_child.data:
        return

    mtm = relational_parent.data.many_to_many.all()
    oto = relational_parent.data.one_to_one
    mto = relational_parent.data.many_to_one.all()
    fk = foriegn_child.data.parent

    return html.div(
        {
            "id": "async-relational-query",
            "data-success": bool(mtm) and bool(oto) and bool(mto) and bool(fk),
        },
        html.p(inspect.currentframe().f_code.co_name),
        html.div(f"Relational Parent Many To Many: {mtm}"),
        html.div(f"Relational Parent One To One: {oto}"),
        html.div(f"Relational Parent Many to One: {mto}"),
        html.div(f"Relational Child Foreign Key: {fk}"),
        html.hr(),
    )


def get_todo_query():
    return TodoItem.objects.all()


def add_todo_mutation(text: str):
    existing = TodoItem.objects.filter(text=text).first()
    if existing:
        if existing.done:
            existing.done = False
            existing.save()
        else:
            return False
    else:
        TodoItem(text=text, done=False).save()


def toggle_todo_mutation(item: TodoItem):
    item.done = not item.done
    item.save()


def _render_todo_items(items, toggle_item):
    return html.ul(
        [
            html.li(
                {"id": f"todo-item-{item.text}", "key": item.text},
                item.text,
                html.input(
                    {
                        "id": f"todo-item-{item.text}-checkbox",
                        "type": "checkbox",
                        "checked": item.done,
                        "on_change": lambda event, i=item: toggle_item.execute(i),
                    }
                ),
            )
            for item in items
        ]
    )


@component
def todo_list():
    input_value, set_input_value = hooks.use_state("")
    items = django_idom.hooks.use_query(get_todo_query)
    toggle_item = django_idom.hooks.use_mutation(toggle_todo_mutation)
    add_item = django_idom.hooks.use_mutation(add_todo_mutation, refetch=get_todo_query)

    def on_submit(event):
        if event["key"] == "Enter":
            add_item.execute(text=event["target"]["value"])
            set_input_value("")

    def on_change(event):
        set_input_value(event["target"]["value"])

    if items.error:
        rendered_items = html.h2(f"Error when loading - {items.error}")
    elif items.data is None:
        rendered_items = html.h2("Loading...")
    else:
        rendered_items = html._(
            html.h3("Not Done"),
            _render_todo_items([i for i in items.data if not i.done], toggle_item),
            html.h3("Done"),
            _render_todo_items([i for i in items.data if i.done], toggle_item),
        )

    if add_item.loading:
        mutation_status = html.h2("Working...")
    elif add_item.error:
        mutation_status = html.h2(f"Error when adding - {add_item.error}")
    else:
        mutation_status = ""  # type: ignore

    return html.div(
        {"id": "todo-list"},
        html.p(inspect.currentframe().f_code.co_name),  # type: ignore
        html.label("Add an item:"),
        html.input(
            {
                "type": "text",
                "id": "todo-input",
                "value": input_value,
                "on_key_press": on_submit,
                "on_change": on_change,
            }
        ),
        mutation_status,
        rendered_items,
        html.hr(),
    )


async def async_get_todo_query():
    return await database_sync_to_async(
        AsyncTodoItem.objects.all, thread_sensitive=False
    )()


async def async_add_todo_mutation(text: str):
    existing = await AsyncTodoItem.objects.filter(text=text).afirst()
    if existing:
        if existing.done:
            existing.done = False
            await database_sync_to_async(existing.save, thread_sensitive=False)()
        else:
            return False
    else:
        await database_sync_to_async(
            AsyncTodoItem(text=text, done=False).save, thread_sensitive=False
        )()


async def async_toggle_todo_mutation(item: AsyncTodoItem):
    item.done = not item.done
    await database_sync_to_async(item.save, thread_sensitive=False)()


@component
def async_todo_list():
    input_value, set_input_value = hooks.use_state("")
    items = django_idom.hooks.use_query(async_get_todo_query)
    toggle_item = django_idom.hooks.use_mutation(async_toggle_todo_mutation)
    add_item = django_idom.hooks.use_mutation(
        async_add_todo_mutation, refetch=async_get_todo_query
    )

    async def on_submit(event):
        if event["key"] == "Enter":
            add_item.execute(text=event["target"]["value"])
            set_input_value("")

    async def on_change(event):
        set_input_value(event["target"]["value"])

    if items.error:
        rendered_items = html.h2(f"Error when loading - {items.error}")
    elif items.data is None:
        rendered_items = html.h2("Loading...")
    else:
        rendered_items = html._(
            html.h3("Not Done"),
            _render_todo_items([i for i in items.data if not i.done], toggle_item),
            html.h3("Done"),
            _render_todo_items([i for i in items.data if i.done], toggle_item),
        )

    if add_item.loading:
        mutation_status = html.h2("Working...")
    elif add_item.error:
        mutation_status = html.h2(f"Error when adding - {add_item.error}")
    else:
        mutation_status = ""  # type: ignore

    return html.div(
        {"id": "async-todo-list"},
        html.p(inspect.currentframe().f_code.co_name),  # type: ignore
        html.label("Add an item:"),
        html.input(
            {
                "type": "text",
                "id": "async-todo-input",
                "value": input_value,
                "on_key_press": on_submit,
                "on_change": on_change,
            }
        ),
        mutation_status,
        rendered_items,
        html.hr(),
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
            {
                "id": f"{inspect.currentframe().f_code.co_name}_btn",  # type: ignore
                "on_click": on_click,
            },
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
            {
                "id": f"{inspect.currentframe().f_code.co_name}_btn",  # type: ignore
                "on_click": on_click,
            },
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
            {
                "id": f"{inspect.currentframe().f_code.co_name}_btn",  # type: ignore
                "on_click": on_click,
            },
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
