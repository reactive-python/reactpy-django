import idom
from django.http import HttpResponse
from django.template import loader


def base_template(request):
    template = loader.get_template("base.html")
    context = {}
    return HttpResponse(template.render(context, request))


@idom.component
def Root():
    return idom.html.div(HelloWorld(), Counter())


@idom.component
def HelloWorld():
    return idom.html.h1({"id": "hello-world"}, "Hello World!")


@idom.component
def Counter():
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
