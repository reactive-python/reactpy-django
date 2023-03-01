<!--header-start-->

# Django-ReactPy &middot; [![Tests](https://github.com/reactive-python/django-reactpy/workflows/Test/badge.svg?event=push)](https://github.com/reactive-python/django-reactpy/actions?query=workflow%3ATest) [![PyPI Version](https://img.shields.io/pypi/v/django-reactpy.svg?label=PyPI)](https://pypi.python.org/pypi/django-reactpy) [![License](https://img.shields.io/badge/License-MIT-purple.svg)](https://github.com/reactive-python/django-reactpy/blob/main/LICENSE) [![Docs](https://img.shields.io/website?down_message=offline&label=Docs&logo=read%20the%20docs&logoColor=white&up_message=online&url=https%3A%2F%2Freactive-python.github.io%2Fdjango-reactpy%2F)](https://reactive-python.github.io/django-reactpy/)

<!--header-end-->
<!--intro-start-->

Django-ReactPy connects your Python project to a ReactJS front-end, allowing you to create **interactive websites without needing JavaScript!**

Following ReactJS styling, web elements are combined into [reusable "components"](https://reactpy.dev/docs/guides/creating-interfaces/your-first-components/index.html#parametrizing-components). These components can utilize [hooks](https://reactpy.dev/docs/reference/hooks-api.html) and [events](https://reactpy.dev/docs/guides/adding-interactivity/responding-to-events/index.html#async-event-handlers) to create infinitely complex web pages.

When needed, ReactPy can [use components directly from NPM](https://reactpy.dev/docs/guides/escape-hatches/javascript-components.html#dynamically-loaded-components). For additional flexibility, components can also be [fully developed in JavaScript](https://reactpy.dev/docs/guides/escape-hatches/javascript-components.html#custom-javascript-components).

Any Python web framework with Websockets can support ReactPy. See below for what frameworks are supported out of the box.

| Supported Frameworks | Supported Frameworks (External) |
| --- | --- |
| [`Flask`, `FastAPI`, `Sanic`, `Tornado`](https://reactpy.dev/docs/guides/getting-started/installing-reactpy.html#officially-supported-servers) | [`Django`](https://github.com/reactive-python/django-reactpy), [`Plotly-Dash`](https://github.com/reactive-python/reactpy-dash), [`Jupyter`](https://github.com/reactive-python/reactpy-jupyter) |

<!--intro-end-->

# At a Glance

## `my_app/components.py`

<!--py-header-start-->

You will need a file to define your [ReactPy](https://github.com/reactive-python/reactpy) components. We recommend creating a `components.py` file within your chosen **Django app** to start out. Within this file, we will create a simple `hello_world` component.

<!--py-header-end-->
<!--py-code-start-->

```python
from reactpy import component, html

@component
def hello_world(recipient: str):
    return html.h1(f"Hello {recipient}!")
```

<!--py-code-end-->

## [`my_app/templates/my-template.html`](https://docs.djangoproject.com/en/dev/topics/templates/)

<!--html-header-start-->

In your **Django app**'s HTML template, you can now embed your ReactPy component using the `component` template tag. Within this tag, you will need to type in your dotted path to the component function as the first argument.

Additionally, you can pass in `args` and `kwargs` into your component function. For example, after reading the code below, pay attention to how the function definition for `hello_world` (_in the previous example_) accepts a `recipient` argument.

<!--html-header-end-->
<!--html-code-start-->

```jinja
{% load reactpy %}
<!DOCTYPE html>
<html>
  <body>
    {% component "example_project.my_app.components.hello_world" recipient="World" %}
  </body>
</html>
```

<!--html-code-end-->

# Resources

<!--resources-start-->

Follow the links below to find out more about this project.

-   [Try it Now](https://mybinder.org/v2/gh/reactive-python/reactpy-jupyter/main?urlpath=lab/tree/notebooks/introduction.ipynb) - Check out ReactPy in a Jupyter Notebook.
-   [Documentation](https://reactive-python.github.io/django-reactpy) - Learn how to install, run, and use ReactPy.
-   [Community Forum](https://github.com/reactive-python/reactpy/discussions) - Ask questions, share ideas, and show off projects.

<!--resources-end-->
