import idom

import django_idom

from . import views


@idom.component
def HelloWorld():
    return idom.html.h1({"id": "hello-world"}, "Hello World!")


@idom.component
def Button():
    count, set_count = idom.hooks.use_state(0)
    return idom.html.div(
        idom.html.button(
            {"id": "counter-inc", "onClick": lambda event: set_count(count + 1)},
            "Click me!",
        ),
        idom.html.p(
            {"id": "counter-num", "data-count": count},
            f"Current count is: {count}",
        ),
    )


@idom.component
def ParametrizedComponent(x, y):
    total = x + y
    return idom.html.h1({"id": "parametrized-component", "data-value": total}, total)


victory = idom.web.module_from_template("react", "victory-bar", fallback="...")
VictoryBar = idom.web.export(victory, "VictoryBar")


@idom.component
def SimpleBarChart():
    return VictoryBar()


@idom.component
def UseWebsocket():
    ws = django_idom.hooks.use_websocket()
    ws.scope = "..."
    success = bool(ws.scope and ws.close and ws.disconnect and ws.view_id)
    return idom.html.div(
        {"id": "use-websocket", "data-success": success},
        idom.html.hr(),
        f"UseWebsocket: {ws}",
        idom.html.hr(),
    )


@idom.component
def UseScope():
    scope = django_idom.hooks.use_scope()
    success = len(scope) >= 10 and scope["type"] == "websocket"
    return idom.html.div(
        {"id": "use-scope", "data-success": success},
        f"UseScope: {scope}",
        idom.html.hr(),
    )


@idom.component
def UseLocation():
    location = django_idom.hooks.use_location()
    success = bool(location)
    return idom.html.div(
        {"id": "use-location", "data-success": success},
        f"UseLocation: {location}",
        idom.html.hr(),
    )


@idom.component
def StaticCSS():
    return idom.html.div(
        {"id": "static-css"},
        django_idom.components.DjangoCSS("static-css-test.css"),
        idom.html.div({"style": {"display": "inline"}}, "StaticCSS: "),
        idom.html.button("This text should be blue."),
        idom.html.hr(),
    )


@idom.component
def StaticJS():
    success = False
    return idom.html._(
        idom.html.div(
            {"id": "static-js", "data-success": success},
            f"StaticJS: {success}",
            django_idom.components.DjangoJS("static-js-test.js"),
        ),
        idom.html.hr(),
    )


@idom.component
def ViewToComponent():
    return django_idom.utils.view_to_component(views.view_to_component)


@idom.component
def ViewToComponentAsync():
    return django_idom.utils.view_to_component(views.view_to_component_async)


@idom.component
def ViewToComponentClass():
    return django_idom.utils.view_to_component(views.ViewToComponentClass)


@idom.component
def ViewToComponentCompatibility():
    return idom.html.div(
        {"id": "view_to_component_compatibility"},
        django_idom.utils.view_to_component(
            views.view_to_component_compatibility, compatibility=True
        ),
        idom.html.hr(),
    )


@idom.component
def ViewToComponentMiddleware():
    def str_replace_middleware(view):
        def middleware(request, *args, **kwargs):
            render = view(request, *args, **kwargs)
            render.content = render.content.decode("utf-8").replace("_not_working", "")
            return render

        return middleware

    return django_idom.utils.view_to_component(
        views.view_to_component_middleware, middleware=[str_replace_middleware]
    )


@idom.component
def ViewToComponentScripts():
    return django_idom.utils.view_to_component(views.view_to_component_scripts)
