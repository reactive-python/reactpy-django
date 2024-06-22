import asyncio
import inspect
from pathlib import Path

import reactpy_django
from channels.auth import login, logout
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.shortcuts import render
from reactpy import component, hooks, html, web
from reactpy_django.components import view_to_component, view_to_iframe

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

from . import views
from .types import TestObject


@component
def hello_world():
    return html._(html.div({"id": "hello-world"}, "Hello World!"))


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
        )
    )


@component
def parameterized_component(x, y):
    total = x + y
    return html._(
        html.div(
            {"id": "parametrized-component", "data-value": total},
            f"parameterized_component: {total}",
        )
    )


@component
def object_in_templatetag(my_object: TestObject):
    success = bool(my_object and my_object.value)
    co_name = inspect.currentframe().f_code.co_name  # type: ignore
    return html._(
        html.div(
            {"id": co_name, "data-success": success}, f"{co_name}: ", str(my_object)
        )
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
    return html._("simple_button:", SimpleButton({"id": "simple-button"}))


@component
def use_connection():
    ws = reactpy_django.hooks.use_connection()
    success = bool(
        ws.scope
        and getattr(ws, "location", None)
        and getattr(ws.carrier, "close", None)
        and getattr(ws.carrier, "disconnect", None)
        and getattr(ws.carrier, "dotted_path", None)
    )
    return html.div(
        {"id": "use-connection", "data-success": success}, f"use_connection: {ws}"
    )


@component
def use_scope():
    scope = reactpy_django.hooks.use_scope()
    success = len(scope) >= 10 and scope["type"] == "websocket"
    return html.div({"id": "use-scope", "data-success": success}, f"use_scope: {scope}")


@component
def use_location():
    location = reactpy_django.hooks.use_location()
    success = bool(location)
    return html.div(
        {"id": "use-location", "data-success": success}, f"use_location: {location}"
    )


@component
def use_origin():
    origin = reactpy_django.hooks.use_origin()
    success = bool(origin)
    return html.div(
        {"id": "use-origin", "data-success": success}, f"use_origin: {origin}"
    )


@component
def django_css():
    return html.div(
        {"id": "django-css"},
        reactpy_django.components.django_css("django-css-test.css", key="test"),
        html.div({"style": {"display": "inline"}}, "django_css: "),
        html.button("This text should be blue."),
    )


@component
def django_js():
    success = False
    return html._(
        html.div(
            {"id": "django-js", "data-success": success},
            f"django_js: {success}",
            reactpy_django.components.django_js("django-js-test.js", key="test"),
        )
    )


@component
@reactpy_django.decorators.auth_required(
    fallback=html.div(
        {"id": "unauthorized-user-fallback"}, "unauthorized_user: Success"
    )
)
def unauthorized_user():
    return html.div({"id": "unauthorized-user"}, "unauthorized_user: Fail")


@component
@reactpy_django.decorators.auth_required(
    auth_attribute="is_anonymous",
    fallback=html.div({"id": "authorized-user-fallback"}, "authorized_user: Fail"),
)
def authorized_user():
    return html.div({"id": "authorized-user"}, "authorized_user: Success")


@reactpy_django.decorators.user_passes_test(
    lambda user: user.is_anonymous,
    fallback=html.div(
        {"id": "authorized-user-test-fallback"}, "authorized_user_test: Fail"
    ),
)
@component
def authorized_user_test():
    return html.div({"id": "authorized-user-test"}, "authorized_user_test: Success")


@reactpy_django.decorators.user_passes_test(
    lambda user: user.is_active,
    fallback=html.div(
        {"id": "unauthorized-user-test-fallback"}, "unauthorized_user_test: Success"
    ),
)
@component
def unauthorized_user_test():
    return html.div({"id": "unauthorized-user-test"}, "unauthorized_user_test: Fail")


@reactpy_django.decorators.user_passes_test(lambda user: True)
def incorrect_user_passes_test_decorator():
    return html.div("incorrect_decorator_test: Fail")


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
    foriegn_child = reactpy_django.hooks.use_query(get_foriegn_child_query)
    relational_parent = reactpy_django.hooks.use_query(get_relational_parent_query)

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
        html.p(inspect.currentframe().f_code.co_name),  # type: ignore
        html.div(f"Relational Parent Many To Many: {mtm}"),
        html.div(f"Relational Parent One To One: {oto}"),
        html.div(f"Relational Parent Many to One: {mto}"),
        html.div(f"Relational Child Foreign Key: {fk}"),
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
    await parent.many_to_many.aset((child_1, child_2, child_3))
    await parent.asave()
    return parent


async def async_get_relational_parent_query():
    # Sleep to avoid race conditions in the test
    # Also serves as a good way of testing whether things are truly async
    await asyncio.sleep(2)
    return await async_get_or_create_relational_parent()


async def async_get_foriegn_child_query():
    child = await AsyncForiegnChild.objects.afirst()
    if not child:
        parent = await async_get_or_create_relational_parent()
        child = await AsyncForiegnChild.objects.acreate(
            parent=parent, text="Foriegn Child"
        )
        await child.asave()
    return child


@component
def async_relational_query():
    foriegn_child = reactpy_django.hooks.use_query(async_get_foriegn_child_query)
    relational_parent = reactpy_django.hooks.use_query(
        async_get_relational_parent_query
    )

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
        html.p(inspect.currentframe().f_code.co_name),  # type: ignore
        html.div(f"Relational Parent Many To Many: {mtm}"),
        html.div(f"Relational Parent One To One: {oto}"),
        html.div(f"Relational Parent Many to One: {mto}"),
        html.div(f"Relational Child Foreign Key: {fk}"),
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
                        "on_change": lambda event, i=item: toggle_item(i),
                    }
                ),
            )
            for item in items
        ]
    )


@component
def todo_list():
    input_value, set_input_value = hooks.use_state("")
    items = reactpy_django.hooks.use_query(get_todo_query)
    toggle_item = reactpy_django.hooks.use_mutation(toggle_todo_mutation)
    add_item = reactpy_django.hooks.use_mutation(
        add_todo_mutation, refetch=get_todo_query
    )

    def on_submit(event):
        if event["key"] == "Enter":
            add_item(text=event["target"]["value"])
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
    )


async def async_get_todo_query():
    return await database_sync_to_async(AsyncTodoItem.objects.all)()


async def async_add_todo_mutation(text: str):
    existing = await AsyncTodoItem.objects.filter(text=text).afirst()
    if existing:
        if existing.done:
            existing.done = False
            await existing.asave()
        else:
            return False
    else:
        await AsyncTodoItem(text=text, done=False).asave()


async def async_toggle_todo_mutation(item: AsyncTodoItem):
    item.done = not item.done
    await item.asave()


@component
def async_todo_list():
    input_value, set_input_value = hooks.use_state("")
    items = reactpy_django.hooks.use_query(async_get_todo_query)
    toggle_item = reactpy_django.hooks.use_mutation(async_toggle_todo_mutation)
    add_item = reactpy_django.hooks.use_mutation(
        async_add_todo_mutation, refetch=async_get_todo_query
    )

    async def on_submit(event):
        if event["key"] == "Enter":
            add_item(text=event["target"]["value"])
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
    )


view_to_component_sync_func = view_to_component(views.view_to_component_sync_func)
view_to_component_async_func = view_to_component(views.view_to_component_async_func)
view_to_component_sync_class = view_to_component(
    views.ViewToComponentSyncClass.as_view()
)
view_to_component_async_class = view_to_component(
    views.ViewToComponentAsyncClass.as_view()
)
view_to_component_template_view_class = view_to_component(
    views.ViewToComponentTemplateViewClass.as_view()
)
_view_to_component_sync_func_compatibility = view_to_component(
    views.view_to_component_sync_func_compatibility, compatibility=True
)
_view_to_component_async_func_compatibility = view_to_component(
    views.view_to_component_async_func_compatibility, compatibility=True
)
_view_to_component_sync_class_compatibility = view_to_component(
    views.ViewToComponentSyncClassCompatibility.as_view(), compatibility=True
)
_view_to_component_async_class_compatibility = view_to_component(
    views.ViewToComponentAsyncClassCompatibility.as_view(), compatibility=True
)
_view_to_component_template_view_class_compatibility = view_to_component(
    views.ViewToComponentTemplateViewClassCompatibility.as_view(), compatibility=True
)
_view_to_iframe_args = view_to_iframe(views.view_to_iframe_args)
_view_to_iframe_not_registered = view_to_iframe("view_does_not_exist")
view_to_component_script = view_to_component(views.view_to_component_script)
_view_to_component_request = view_to_component(views.view_to_component_request)
_view_to_component_args = view_to_component(views.view_to_component_args)
_view_to_component_kwargs = view_to_component(views.view_to_component_kwargs)


@component
def view_to_component_sync_func_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_sync_func_compatibility(key="test"),
    )


@component
def view_to_component_async_func_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_async_func_compatibility(),
    )


@component
def view_to_component_sync_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_sync_class_compatibility(),
    )


@component
def view_to_component_async_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_async_class_compatibility(),
    )


@component
def view_to_component_template_view_class_compatibility():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_component_template_view_class_compatibility(),
    )


@component
def view_to_iframe_args():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_iframe_args("Arg1", "Arg2", kwarg1="Kwarg1", kwarg2="Kwarg2"),
    )


@component
def view_to_iframe_not_registered():
    return html.div(
        {"id": inspect.currentframe().f_code.co_name},  # type: ignore
        _view_to_iframe_not_registered(),
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


@component
def custom_host(number=0):
    scope = reactpy_django.hooks.use_scope()
    port = scope["server"][1]

    return html.div(
        {
            "class_name": f"{inspect.currentframe().f_code.co_name}-{number}",  # type: ignore
            "data-port": port,
        },
        f"Server Port: {port}",
    )


@component
def broken_postprocessor_query():
    relational_parent = reactpy_django.hooks.use_query(
        get_relational_parent_query, postprocessor=None
    )

    if not relational_parent.data:
        return

    mtm = relational_parent.data.many_to_many.all()

    return html.div(f"This should have failed! Something went wrong: {mtm}")


def get_or_create_user1():
    return get_user_model().objects.get_or_create(username="user_1")[0]


def get_or_create_user2():
    return get_user_model().objects.get_or_create(username="user_2")[0]


@component
def use_user_data():
    user_data_query, user_data_mutation = reactpy_django.hooks.use_user_data()
    user1 = reactpy_django.hooks.use_query(get_or_create_user1)
    user2 = reactpy_django.hooks.use_query(get_or_create_user2)
    current_user = reactpy_django.hooks.use_user()
    scope = reactpy_django.hooks.use_scope()

    async def login_user1(event):
        await login(scope, user1.data)
        user_data_query.refetch()
        user_data_mutation.reset()

    async def login_user2(event):
        await login(scope, user2.data)
        user_data_query.refetch()
        user_data_mutation.reset()

    async def logout_user(event):
        await logout(scope)
        user_data_query.refetch()
        user_data_mutation.reset()

    async def clear_data(event):
        user_data_mutation({})
        user_data_query.refetch()
        user_data_mutation.reset()

    async def on_submit(event):
        if event["key"] == "Enter":
            user_data_mutation(
                (user_data_query.data or {})
                | {event["target"]["value"]: event["target"]["value"]}
            )

    return html.div(
        {
            "id": "use-user-data",
            "data-success": bool(user_data_query.data),
            "data-fetch-error": bool(user_data_query.error),
            "data-mutation-error": bool(user_data_mutation.error),
            "data-loading": user_data_query.loading or user_data_mutation.loading,
            "data-username": (
                "AnonymousUser" if current_user.is_anonymous else current_user.username
            ),
        },
        html.div("use_user_data"),
        html.button({"className": "login-1", "on_click": login_user1}, "Login 1"),
        html.button({"className": "login-2", "on_click": login_user2}, "Login 2"),
        html.button({"className": "logout", "on_click": logout_user}, "Logout"),
        html.button({"className": "clear", "on_click": clear_data}, "Clear Data"),
        html.div(f"User: {current_user}"),
        html.div(f"Data: {user_data_query.data}"),
        html.div(
            f"Data State: (loading={user_data_query.loading}, error={user_data_query.error})"
        ),
        html.div(
            f"Mutation State: (loading={user_data_mutation.loading}, error={user_data_mutation.error})"
        ),
        html.div(
            html.input(
                {"on_key_press": on_submit, "placeholder": "Type here to add data"}
            )
        ),
    )


def get_or_create_user3():
    return get_user_model().objects.get_or_create(username="user_3")[0]


@component
def use_user_data_with_default():
    async def value3():
        return "value3"

    def value2():
        return "value2"

    user_data_query, user_data_mutation = reactpy_django.hooks.use_user_data(
        {"default1": "value", "default2": value2, "default3": value3},
        save_default_data=True,
    )
    user3 = reactpy_django.hooks.use_query(get_or_create_user3)
    current_user = reactpy_django.hooks.use_user()
    scope = reactpy_django.hooks.use_scope()

    async def login_user3(event):
        await login(scope, user3.data)
        user_data_query.refetch()
        user_data_mutation.reset()

    async def clear_data(event):
        user_data_mutation({})
        user_data_query.refetch()
        user_data_mutation.reset()

    async def on_submit(event):
        if event["key"] == "Enter":
            user_data_mutation(
                (user_data_query.data or {})
                | {event["target"]["value"]: event["target"]["value"]}
            )

    return html.div(
        {
            "id": "use-user-data-with-default",
            "data-fetch-error": bool(user_data_query.error),
            "data-mutation-error": bool(user_data_mutation.error),
            "data-loading": user_data_query.loading or user_data_mutation.loading,
            "data-username": (
                "AnonymousUser" if current_user.is_anonymous else current_user.username
            ),
        },
        html.div("use_user_data_with_default"),
        html.button({"className": "login-3", "on_click": login_user3}, "Login 3"),
        html.button({"className": "clear", "on_click": clear_data}, "Clear Data"),
        html.div(f"User: {current_user}"),
        html.div(f"Data: {user_data_query.data}"),
        html.div(
            f"Data State: (loading={user_data_query.loading}, error={user_data_query.error})"
        ),
        html.div(
            f"Mutation State: (loading={user_data_mutation.loading}, error={user_data_mutation.error})"
        ),
        html.div(
            html.input(
                {"on_key_press": on_submit, "placeholder": "Type here to add data"}
            )
        ),
    )
