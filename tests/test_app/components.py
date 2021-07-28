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
