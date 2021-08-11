import idom

from django_idom import register_component


@register_component
def HelloWorld():
    return idom.html.h1({"id": "hello-world"}, "Hello World!")


@register_component
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


@register_component
def ParametrizedComponent(x, y):
    total = x + y
    return idom.html.h1({"id": "parametrized-component", "data-value": total}, total)


victory = idom.web.module_from_template("react", "victory-line", fallback="...")
VictoryBar = idom.web.export(victory, "VictoryBar")


@register_component
def SimpleBarChart():
    return VictoryBar()
