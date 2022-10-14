<!--header-start-->

# Django IDOM &middot; [![Tests](https://github.com/idom-team/django-idom/workflows/Test/badge.svg?event=push)](https://github.com/idom-team/django-idom/actions?query=workflow%3ATest) [![PyPI Version](https://img.shields.io/pypi/v/django-idom.svg)](https://pypi.python.org/pypi/django-idom) [![License](https://img.shields.io/badge/License-MIT-purple.svg)](https://github.com/idom-team/django-idom/blob/main/LICENSE)

<!--header-end-->
<!--intro-start-->

Django-IDOM connects your Python project to a ReactJS frontend, allowing you to create **interactive websites without needing JavaScript!**

Following ReactJS styling, web elements are combined into [reusable "components"](https://idom-docs.herokuapp.com/docs/guides/creating-interfaces/your-first-components/index.html#parametrizing-components). These components can utilize [hooks](https://idom-docs.herokuapp.com/docs/reference/hooks-api.html) and [events](https://idom-docs.herokuapp.com/docs/guides/adding-interactivity/responding-to-events/index.html#async-event-handlers) to create infinitely complex web pages.

When needed, IDOM can [use components directly from NPM](https://idom-docs.herokuapp.com/docs/guides/escape-hatches/javascript-components.html#dynamically-loaded-components). For additional flexibility, components can also be [fully developed in JavaScript](https://idom-docs.herokuapp.com/docs/guides/escape-hatches/javascript-components.html#custom-javascript-components).

Any Python web framework with Websockets can support IDOM. See below for what frameworks are supported out of the box.

| Supported Frameworks | Supported Frameworks (External) |
| --- | --- |
| [`Flask`, `FastAPI`, `Sanic`, `Tornado`](https://idom-docs.herokuapp.com/docs/guides/getting-started/installing-idom.html#officially-supported-servers) | [`Django`](https://github.com/idom-team/django-idom), [`Plotly-Dash`](https://github.com/idom-team/idom-dash), [`Jupyter`](https://github.com/idom-team/idom-jupyter) |

<!--intro-end-->

# At a Glance

## `my_app/components.py`

<!--py-header-start-->

You'll need a file to define your [IDOM](https://github.com/idom-team/idom) components. We recommend creating a `components.py` file within your chosen **Django app** to start out. Within this file, we will create a simple `hello_world` component.

<!--py-header-end-->
<!--py-code-start-->

```python linenums="1"
from idom import component, html

@component
def hello_world(recipient: str):
    return html.h1(f"Hello {recipient}!")
```

<!--py-code-end-->

## [`my_app/templates/my-template.html`](https://docs.djangoproject.com/en/dev/topics/templates/)

<!--html-header-start-->

In your **Django app**'s HTML template, you can now embed your IDOM component using the `component` template tag. Within this tag, you will need to type in your dotted path to the component function as the first argument.

Additonally, you can pass in keyword arguments into your component function. For example, after reading the code below, pay attention to how the function definition for `hello_world` (_in the previous example_) accepts a `recipient` argument.

<!--html-header-end-->
<!--html-code-start-->

```jinja linenums="1"
{% load idom %}
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

-   [Try it Now](https://mybinder.org/v2/gh/idom-team/idom-jupyter/main?urlpath=lab/tree/notebooks/introduction.ipynb) - Check out IDOM in a Jupyter Notebook.
-   [Documentation](https://idom-team.github.io/django-idom) - Learn how to install, run, and use IDOM.
-   [Community Forum](https://github.com/idom-team/idom/discussions) - Ask questions, share ideas, and show off projects.

<!--resources-end-->
