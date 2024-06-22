## Overview

<p class="intro" markdown>

Django template tags can be used within your HTML templates to provide ReactPy features.

</p>

---

## Component

This template tag can be used to insert any number of ReactPy components onto your page.

Each component loaded via this template tag will receive a dedicated WebSocket connection to the server.

=== "my_template.html"

    {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python dotted_path` | `#!python str` | The dotted path to the component to render. | N/A |
    | `#!python *args` | `#!python Any` | The positional arguments to provide to the component. | N/A |
    | `#!python class` | `#!python str | None` | The HTML class to apply to the top-level component div. | `#!python None` |
    | `#!python key` | `#!python Any` | Force the component's root node to use a [specific key value](https://reactpy.dev/docs/guides/creating-interfaces/rendering-data/index.html#organizing-items-with-keys). Using `#!python key` within a template tag is effectively useless. | `#!python None` |
    | `#!python host` | `#!python str | None` | The host to use for ReactPy connections. If unset, the host will be automatically configured.<br/>Example values include: `localhost:8000`, `example.com`, `example.com/subdir` | `#!python None` |
    | `#!python prerender` | `#!python str` | If `#!python "true"` the component will pre-rendered, which enables SEO compatibility and reduces perceived latency. | `#!python "false"` |
    | `#!python offline` | `#!python str` | The dotted path to a component that will be displayed if your root component loses connection to the server. Keep in mind, this `offline` component will be non-interactive (hooks won't operate). | `#!python ""` |
    | `#!python **kwargs` | `#!python Any` | The keyword arguments to provide to the component. | N/A |

<!--context-start-->

??? warning "Do not use context variables for the component path"

    The ReactPy component finder requires that your component path is a string.

    **Do not** use Django template/context variables for the component path. Failure to follow this warning will result in render failures.

    For example, **do not** do the following:

    === "my_template.html"

        ```jinja
        <!-- This is good -->
        {% component "example_project.my_app.components.hello_world" recipient="World" %}

        <!-- This is bad -->
        {% component my_variable recipient="World" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/template-tag-bad-view.py" %}
        ```

    _Note: If you decide to not follow this warning, you will need to use the [`register_component`](../reference/utils.md#register-component) function to manually register your components._

<!--context-end-->

<!--multiple-components-start-->

??? question "Can I use multiple components on one page?"

    You can add as many components to a webpage as needed by using the template tag multiple times. Retrofitting legacy sites to use ReactPy will typically involve many components on one page.

    === "my_template.html"

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

??? question "Can I use positional arguments instead of keyword arguments?"

    You can use any combination of `#!python *args`/`#!python **kwargs` in your template tag.

    === "my_template.html"

        ```jinja
        {% component "example_project.my_app.components.frog_greeter" 123 "Mr. Froggles" species="Grey Treefrog" %}
        ```

    === "components.py"

        ```python
        {% include "../../examples/python/template-tag-args-kwargs.py" %}
        ```

??? question "Can I render components on a different server (distributed computing)?"

    Yes! This is most commonly done through [`settings.py:REACTPY_HOSTS`](../reference/settings.md#reactpy_default_hosts). However, you can use the `#!python host` keyword to render components on a specific ASGI server.

    === "my_template.html"

        ```jinja
        ...
        {% component "example_project.my_app.components.do_something" host="127.0.0.1:8001" %}
        ...
        ```

    This configuration most commonly involves you deploying multiple instances of your project. But, you can also create dedicated Django project(s) that only render specific ReactPy components if you wish.

    Here's a couple of things to keep in mind:

    1. If your host address are completely separate ( `origin1.com != origin2.com` ) you will need to [configure CORS headers](https://pypi.org/project/django-cors-headers/) on your main application during deployment.
    2. You will not need to register ReactPy WebSocket or HTTP paths on any applications that do not perform any component rendering.
    3. Your component will only be able to access your template tag's `#!python *args`/`#!python **kwargs` if your applications share a common database.

??? question "How do I pre-render components for SEO compatibility?"

    This is most commonly done through [`settings.py:REACTPY_PRERENDER`](../reference/settings.md#reactpy_prerender). However, you can use the `#!python prerender` keyword to pre-render a specific component.

    === "my_template.html"

        ```jinja
        ...
        {% component "example_project.my_app.components.do_something" prerender="true" %}
        ...
        ```

??? question "How do I display something when the client disconnects?"

    You can use the `#!python offline` keyword to display a specific component when the client disconnects from the server.

    === "my_template.html"

        ```jinja
        ...
        {% component "example_project.my_app.components.do_something" offline="example_project.my_app.components.offline" %}
        ...
        ```

    _Note: The `#!python offline` component will be non-interactive (hooks won't operate)._

## PyScript Component

This template tag can be used to insert any number of **client-side** ReactPy components onto your page.

<!--pyscript-def-start-->

By default, the only dependencies available are the Python standard library, `pyscript`, `pyodide`, `reactpy` core.

Your PyScript component file requires a `#!python def root()` component to function as the entry point.

<!--pyscript-def-end-->

!!! warning "Pitfall"

    Your provided Python file is loaded directly into the client (web browser) **as raw text**, and ran using a PyScript interpreter. Be cautious about what you include in your Python file.

    As a result of running client-side, Python packages within your local environment (such as those installed via `pip install ...`)  are **not accessible** within PyScript components.

=== "my_template.html"

    ```jinja
    {% include "../../examples/html/pyscript-component.html" %}
    ```

=== "hello_world.py"

    ```python
    {% include "../../examples/python/pyscript-hello-world.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python *file_paths` | `#!python str` | File path to your client-side component. If multiple paths are provided, the contents are automatically merged. | N/A |
    | `#!python initial` | `#!python str | VdomDict | ComponentType` | The initial HTML that is displayed prior to the PyScript component loads. This can either be a string containing raw HTML, a `#!python reactpy.html` snippet, or a non-interactive component. | `#!python ""` |
    | `#!python root` | `#!python str` | The name of the root component function. | `#!python "root"` |

<!--pyscript-js-exec-start-->

??? question "How do I execute JavaScript within PyScript components?"

    PyScript components have the ability to directly execute standard library JavaScript using the [`pyodide` `js` module](https://pyodide.org/en/stable/usage/type-conversions.html#importing-javascript-objects-into-python) or [`pyscript` foreign function interface](https://docs.pyscript.net/2024.6.1/user-guide/dom/).

    The `#!python js` module has access to everything within the browser's JavaScript environment. Therefore, any global JavaScript functions loaded within your HTML `#!html <head>` can be called as well. However, be mindful of JavaScript load order!

    === "root.py"

        ```python
        {% include "../../examples/python/pyscript-js-execution.py" %}
        ```

    To import JavaScript modules in a fashion similar to `#!javascript import {moment} from 'static/moment.js'`, you will need to configure your `#!jinja {% pyscript_setup %}` block to make the module available to PyScript. This module will be accessed within `#!python pyscript.js_modules.*`. For more information, see the [PyScript JS modules docs](https://docs.pyscript.net/2024.6.2/user-guide/configuration/#javascript-modules).

    === "root.py"

        ```python
        {% include "../../examples/python/pyscript-js-module.py" %}
        ```

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-js-module.html" %}
        ```

<!--pyscript-js-exec-end-->

<!--pyscript-multifile-start-->

??? question "Does my entire component need to be contained in one file?"

    Splitting a large file into multiple files is a common practice in software development.

    However, PyScript components are run on the client browser. As such, they do not have access to your local development environment, and thus cannot `#!python import` any local Python files.

    If your PyScript component file gets too large, you can declare multiple file paths instead. These files will automatically combined by ReactPy.

    Here is how we recommend splitting your component into multiple files while avoiding local imports but retaining type hints.

    <!--pyscript-multifile-end-->

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-multiple-files.html" %}
        ```

    === "root.py"

        ```python
        {% include "../../examples/python/pyscript-multiple-files-root.py" %}
        ```

    === "child.py"

        ```python
        {% include "../../examples/python/pyscript-multiple-files-child.py" %}
        ```

??? question "How do I display something while the component is loading?"

    You can configure the `#!python initial` keyword to display HTML while your PyScript component is loading.

    The value for `#!python initial` is most commonly be a string containing raw HTML.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-initial-string.html" %}
        ```

    However, you can also insert a `#!python reactpy.html` snippet or a non-interactive `#!python @component` via template context.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-initial-object.html" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/pyscript-initial-object.py" %}
        ```

??? question "Can I use a different name for my root component?"

    Yes, you can use the `#!python root` keyword to specify a different name for your root function.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-root.html" %}
        ```

    === "main.py"

        ```python
        {% include "../../examples/python/pyscript-root.py" %}
        ```

## PyScript Setup

This template tag configures the current page to be able to run `pyscript`.

You can optionally use this tag to configure the current PyScript environment. For example, you can include a list of Python packages to automatically install within the PyScript environment.

=== "my_template.html"

    ```jinja
    {% include "../../examples/html/pyscript-setup.html" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python *extra_py` | `#!python str` | Dependencies that need to be loaded on the page for your PyScript components. Each dependency must be contained within it's own string and written in Python requirements file syntax. | N/A |
    | `#!python extra_js` | `#!python str | dict` | A JSON string or Python dictionary containing a vanilla JavaScript module URL and the `#!python name: str` to access it within `#!python pyscript.js_modules.*`. | `#!python ""` |
    | `#!python config` | `#!python str | dict` | A JSON string or Python dictionary containing PyScript configuration values. | `#!python ""` |

??? question "How do I install additional Python dependencies?"

    Dependencies must be available on [`pypi`](https://pypi.org/) and declared in your `#!jinja {% pyscript_setup %}` block using Python requirements file syntax.

    These dependencies are automatically downloaded and installed into the PyScript client-side environment when the page is loaded.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-setup-dependencies.html" %}
        ```

??? question "How do I install additional Javascript dependencies?"

    You can use the `#!python extra_js` keyword to load additional JavaScript modules into your PyScript environment.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-setup-extra-js-object.html" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/pyscript-setup-extra-js-object.py" %}
        ```

    The value for `#!python extra_js` is most commonly a Python dictionary, but JSON strings are also supported.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-setup-extra-js-string.html" %}
        ```

??? question "How do I modify the `pyscript` default configuration?"

    You can modify the default [PyScript configuration](https://docs.pyscript.net/2024.6.2/user-guide/configuration/) by providing a value to the `#!python config` keyword.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-setup-config-string.html" %}
        ```

    While this value is most commonly a JSON string, Python dictionary objects are also supported.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-setup-config-object.html" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/pyscript-setup-config-object.py" %}
        ```
