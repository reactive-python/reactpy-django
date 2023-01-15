???+ summary

    Template tags can be used within your Django templates such as `my-template.html` to import IDOM features.

## Component

The `component` template tag can be used to insert any number of IDOM components onto your page.

=== "my-template.html"

    {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

<!--context-start-->

??? warning "Do not use context variables for the IDOM component name"

    Our preprocessor relies on the template tag containing a string.

    **Do not** use Django template/context variables for the component path. Failure to follow this warning will result in unexpected behavior.

    For example, **do not** do the following:

    === "my-template.html"

        ```jinja
        <!-- This is bad -->
        {% component dont_do_this recipient="World" %}

        <!-- This is good -->
        {% component "example_project.my_app.components.hello_world" recipient="World" %}
        ```

    === "views.py"

        ```python
        def example_view():
            context_vars = {"dont_do_this": "example_project.my_app.components.hello_world"}
            return render(request, "my-template.html", context_vars)
        ```

<!--context-end-->
<!--kwarg-start-->

??? info "Reserved keyword arguments: `class` and `key`"

    For this template tag, there are two reserved keyword arguments: `class` and `key`

    -   `class` allows you to apply a HTML class to the top-level component div. This is useful for styling purposes.
    -   `key` allows you to force the component to use a [specific key value](https://idom-docs.herokuapp.com/docs/guides/creating-interfaces/rendering-data/index.html#organizing-items-with-keys). Using `key` within a template tag is effectively useless.

    === "my-template.html"

        ```jinja
        ...
        {% component "example.components.my_component" class="my-html-class" key=123 %}
        ...
        ```

<!--kwarg-end-->

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `dotted_path` | `str` | The dotted path to the component to render. | N/A |
    | `*args` | `Any` | The positional arguments to provide to the component. | N/A |
    | `**kwargs` | `Any` | The keyword arguments to provide to the component. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |

<!--multiple-components-start-->

??? question "Can I use multiple components on one page?"

    You can add as many components to a webpage as needed by using the template tag multiple times. Retrofitting legacy sites to use IDOM will typically involve many components on one page.

    === "my-template.html"

        ```jinja
        {% load idom %}
        <!DOCTYPE html>
        <html>
            <body>
            {% component "example_project.my_app.components.hello_world" recipient="World" %}
            {% component "example_project.my_app_2.components.class_component" class="bold small-font" %}
            <div>{% component "example_project.my_app_3.components.simple_component" %}</div>
            </body>
        </html>
        ```

    Please note that components separated like this will not be able to interact with each other, except through database queries.

    Additionally, in scenarios where you are trying to create a Single Page Application (SPA) within Django, you will only have one component within your `#!html <body>` tag.

<!--multiple-components-end-->
