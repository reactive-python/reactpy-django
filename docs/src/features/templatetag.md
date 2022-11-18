???+ summary

    Template tags can be used within your Django templates such as `my-template.html` to import IDOM features.

## Component

=== "my-template.html"

    {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

<!--context-start-->

??? warning "Do not use context variables for the IDOM component name"

    Our pre-processor relies on the template tag containing a string.

    **Do not** use Django template/context variables for the component path. Failure to follow this warning will result in unexpected behavior.

    For example, **do not** do the following:

    === "my-template.html"

        ```jinja linenums="1"
        <!-- This is bad -->
        {% component dont_do_this recipient="World" %}

        <!-- This is good -->
        {% component "example_project.my_app.components.hello_world" recipient="World" %}
        ```

    === "views.py"

        ```python linenums="1"
        def example_view():
            context_vars = {"dont_do_this": "example_project.my_app.components.hello_world"}
            return render(request, "my-template.html", context_vars)
        ```

<!--context-end-->
<!--kwarg-start-->

??? info "Reserved keyword arguments: `class` and `key`"

    For this template tag, there are two reserved keyword arguments: `class` and `key`

    -   `class` allows you to apply a HTML class to the top-level component div. This is useful for styling purposes.
    -   `key` allows you to force the component to use a [specific key value](https://idom-docs.herokuapp.com/docs/guides/understanding-idom/why-idom-needs-keys.html?highlight=key). You typically won't need to set this.

    === "my-template.html"

        ```jinja linenums="1"
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
    | `**kwargs` | `Any` | The keyword arguments to pass to the component. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |

<!--multiple-components-start-->

??? question "Can I use multiple components on one page?"

    You can add as many components to a webpage as needed by using the template tag multiple times. Retrofitting legacy sites to use IDOM will typically involve many components on one page.

    === "my-template.html"

        ```jinja linenums="1"
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

    But keep in mind, in scenarios where you are trying to create a Single Page Application (SPA) within Django, you will only have one central component within your `#!html <body>` tag.

    Additionally, the components in the example above will not be able to interact with each other, except through database queries.

<!--multiple-components-end-->
<!--kwargs-start-->

??? question "Can I use positional arguments instead of keyword arguments?"

    You can only pass in **keyword arguments** within the template tag. Due to technical limitations, **positional arguments** are not supported at this time.

<!--kwargs-end-->
<!--tags-start-->

??? question "What is a "template tag"?"

    You can think of template tags as Django's way of allowing you to run Python code within your HTML. Django-IDOM uses a `#!jinja {% component ... %}` template tag to perform it's magic.

    Keep in mind, in order to use the `#!jinja {% component ... %}` tag, you will need to first call `#!jinja {% load idom %}` to gain access to it.

    === "my-template.html"

        {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

<!--tags-end-->
