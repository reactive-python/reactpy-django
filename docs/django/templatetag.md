Integrated within Django IDOM, we bundle a template tag. Within this tag, you can pass in keyword arguments directly into your component.

{% include-markdown "../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

<!--context-start-->

??? warning "Do not use context variables for the IDOM component name"

       Our pre-processor relies on the template tag containing a string.

       **Do not** use Django context variables for the component path. For example, **do not** do the following:

       ```python title="views.py"
       def example_view():
              context = {"MyVariable": "example_project.my_app.components.HelloComponent"}
              return render(request, "my-template.html", context)
       ```

       ```jinja title="my-template.html"
       ...
       {% component MyVariable recipient="World" %}
       ...
       ```

       Failure to follow this warning will result in a performance penalty and jankiness when using the Django autoreloader.

<!--context-end-->
<!--kwarg-start-->

??? info "Reserved keyword arguments: `class` and `key`"

    For this template tag, there are two reserved keyword arguments: `class` and `key`

    -   `class` allows you to apply a HTML class to the top-level component div. This is useful for styling purposes.
    -   `key` allows you to force the component to use a [specific key value](https://idom-docs.herokuapp.com/docs/guides/understanding-idom/why-idom-needs-keys.html?highlight=key). You typically won't need to set this.

    ```jinja title="my-template.html"
    ...
    {% component "example.components.MyComponent" class="my-html-class" key=123 %}
    ...
    ```

<!--kwarg-end-->
<!--multiple-components-start-->

??? question "Can I use multiple components on one page?"

    You can add as many components to a webpage as needed by using the template tag multiple times. Retrofitting legacy sites to use reactive components will typically involve many components on one page.

    But keep in mind, in scenarios where you are trying to create a Single Page Application (SPA) within Django, you will only have one central component within your body tag as shown below.

<!--multiple-components-end-->
<!--kwargs-start-->

??? question "Can I use positional arguments instead of keyword arguments?"

       You can only pass in **keyword arguments** within the template tag. Due to technical limitations, **positional arguments** are not supported at this time.


<!--kwargs-end-->
