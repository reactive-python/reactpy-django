import idom


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


victory = idom.web.module_from_template("react", "victory", fallback="...")
VictoryBar = idom.web.export(victory, "VictoryBar")


@idom.component
def SimpleBarChart():
    return VictoryBar()
