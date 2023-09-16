## Overview

<p class="intro" markdown>

Django template tags can be used within your HTML templates to provide ReactPy features.

</p>

---

## Component

This template tag can be used to insert any number of ReactPy components onto your page.

=== "my-template.html"

    {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python dotted_path` | `#!python str` | The dotted path to the component to render. | N/A |
    | `#!python *args` | `#!python Any` | The positional arguments to provide to the component. | N/A |
    | `#!python class` | `#!python str | None` | The HTML class to apply to the top-level component div. | `#!python None` |
    | `#!python key` | `#!python Any` | Force the component's root node to use a [specific key value](https://reactpy.dev/docs/guides/creating-interfaces/rendering-data/index.html#organizing-items-with-keys). Using `#!python key` within a template tag is effectively useless. | `#!python None` |
    | `#!python host` | `#!python str | None` | The host to use for the ReactPy connections. If unset, the host will be automatically configured.<br/>Example values include: `localhost:8000`, `example.com`, `example.com/subdir` | `#!python None` |
    | `#!python prerender` | `#!python str` | If `#!python "True"`, the component will pre-rendered, which enables SEO compatibility and reduces perceived latency. | `#!python "False"` |
    | `#!python **kwargs` | `#!python Any` | The keyword arguments to provide to the component. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Component` | A ReactPy component. |

<!--context-start-->

??? warning "Do not use context variables for the component path"

    The ReactPy component finder (`#!python reactpy_django.utils.RootComponentFinder`) requires that your component path is a string.

    **Do not** use Django template/context variables for the component path. Failure to follow this warning can result in unexpected behavior, such as components that will not render.

    For example, **do not** do the following:

    === "my-template.html"

        ```jinja
        <!-- This is good -->
        {% component "example_project.my_app.components.hello_world" recipient="World" %}

        <!-- This is bad -->
        {% component my_variable recipient="World" %}
        ```

    === "views.py"

        ```python
        {% include "../../python/template-tag-bad-view.py" %}
        ```

<!--context-end-->

??? question "Can I render components on a different server (distributed computing)?"

    Yes! By using the `#!python host` keyword argument, you can render components from a completely separate ASGI server.

    === "my-template.html"

        ```jinja
        ...
        {% component "example_project.my_app.components.do_something" host="127.0.0.1:8001" %}
        ...
        ```

    This configuration most commonly involves you deploying multiple instances of your project. But, you can also create dedicated Django project(s) that only render specific ReactPy components if you wish.

    Here's a couple of things to keep in mind:

    1. If your host address are completely separate ( `origin1.com != origin2.com` ) you will need to [configure CORS headers](https://pypi.org/project/django-cors-headers/) on your main application during deployment.
    2. You will not need to register ReactPy HTTP or WebSocket paths on any applications that do not perform any component rendering.
    3. Your component will only be able to access your template tag's `#!python *args`/`#!python **kwargs` if your applications share a common database.

<!--multiple-components-start-->

??? question "Can I use multiple components on one page?"

    You can add as many components to a webpage as needed by using the template tag multiple times. Retrofitting legacy sites to use ReactPy will typically involve many components on one page.

    === "my-template.html"

        ```jinja
        {% load reactpy %}
        <!DOCTYPE html>
        <html>
            <body>
                <h1>{% component "example_project.my_app.components.my_title" %}</h1>
                <p>{% component "example_project.my_app_2.components.goodbye_world" class="bold small-font" %}</p>
                {% component "example_project.my_app_3.components.simple_button" %}
            </body>
        </html>
        ```

    Please note that components separated like this will not be able to interact with each other, except through database queries.

    Additionally, in scenarios where you are trying to create a Single Page Application (SPA) within Django, you will only have one component within your `#!html <body>` tag.

<!--multiple-components-end-->
<!--args-kwargs-start-->

??? question "Can I use positional arguments instead of keyword arguments?"

    You can use any combination of `#!python *args`/`#!python **kwargs` in your template tag.

    === "my-template.html"

        ```jinja
        {% component "example_project.my_app.components.frog_greeter" 123 "Mr. Froggles" species="Grey Treefrog" %}
        ```

    === "components.py"

        ```python
        {% include "../../python/template-tag-args-kwargs.py" %}
        ```

<!--args-kwargs-end-->
