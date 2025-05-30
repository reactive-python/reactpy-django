# <img src="https://raw.githubusercontent.com/reactive-python/reactpy/main/branding/svg/reactpy-logo-square.svg" align="left" height="45"/> ReactPy-Django

<p>
    <a href="https://github.com/reactive-python/reactpy-django/actions/workflows/test-python.yml">
        <img src="https://github.com/reactive-python/reactpy-django/actions/workflows/test-python.yml/badge.svg">
    </a>
    <a href="https://pypi.python.org/pypi/reactpy-django">
        <img src="https://img.shields.io/pypi/v/reactpy-django.svg?label=PyPI">
    </a>
    <a href="https://github.com/reactive-python/reactpy-django/blob/main/LICENSE.md">
        <img src="https://img.shields.io/badge/License-MIT-purple.svg">
    </a>
    <a href="https://reactive-python.github.io/reactpy-django/">
        <img src="https://img.shields.io/website?down_message=offline&label=Docs&logo=read%20the%20docs&logoColor=white&up_message=online&url=https%3A%2F%2Freactive-python.github.io%2Freactpy-django%2F">
    </a>
    <a href="https://discord.gg/uNb5P4hA9X">
        <img src="https://img.shields.io/discord/1111078259854168116?label=Discord&logo=discord">
    </a>
</p>

[ReactPy-Django](https://github.com/reactive-python/reactpy-django) is used to add [ReactPy](https://reactpy.dev/) support to an existing **Django project**. This package also turbocharges ReactPy with features such as...

-   [SEO compatible rendering](https://reactive-python.github.io/reactpy-django/latest/reference/settings/#reactpy_prerender)
-   [Client-Side Python components](https://reactive-python.github.io/reactpy-django/latest/reference/template-tag/#pyscript-component)
-   [Single page application (SPA) capabilities](https://reactive-python.github.io/reactpy-django/latest/reference/router/#django-router)
-   [Distributed computing](https://reactive-python.github.io/reactpy-django/latest/reference/settings/#reactpy_default_hosts)
-   [Performance enhancements](https://reactive-python.github.io/reactpy-django/latest/reference/settings/#performance-settings)
-   [Customizable reconnection behavior](https://reactive-python.github.io/reactpy-django/latest/reference/settings/#stability-settings)
-   [Customizable disconnection behavior](https://reactive-python.github.io/reactpy-django/latest/reference/template-tag)
-   [Multiple root components](https://reactive-python.github.io/reactpy-django/latest/reference/template-tag/)
-   [Cross-process communication/signaling](https://reactive-python.github.io/reactpy-django/latest/reference/hooks/#use-channel-layer)
-   [Django view to ReactPy component conversion](https://reactive-python.github.io/reactpy-django/latest/reference/components/#view-to-component)
-   [Django form to ReactPy component conversion](https://reactive-python.github.io/reactpy-django/latest/reference/components/#django-form)
-   [Django static file access](https://reactive-python.github.io/reactpy-django/latest/reference/components/#django-css)
-   [Django database access](https://reactive-python.github.io/reactpy-django/latest/reference/hooks/#use-query)

## What is ReactPy?

[ReactPy](https://reactpy.dev/) is a library for building user interfaces in Python without Javascript. ReactPy interfaces are made from components that look and behave similar to those found in [ReactJS](https://reactjs.org/). Designed with simplicity in mind, ReactPy can be used by those without web development experience while also being powerful enough to grow with your ambitions.

<table align="center">
    <thead>
        <tr>
            <th colspan="2" style="text-align: center">Supported Backends</th>
        <tr>
            <th style="text-align: center">Built-in</th>
            <th style="text-align: center">External</th>
        </tr>
    </thead>
    <tbody>
        <tr>
        <td>
            <a href="https://reactpy.dev/docs/guides/getting-started/installing-reactpy.html#officially-supported-servers">
                Flask, FastAPI, Sanic, Tornado
            </a>
        </td>
        <td>
            <a href="https://github.com/reactive-python/reactpy-django">Django</a>,
            <a href="https://github.com/reactive-python/reactpy-jupyter">Jupyter</a>,
            <a href="https://github.com/idom-team/idom-dash">Plotly-Dash</a>
        </td>
        </tr>
    </tbody>
</table>

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

## [`my_app/templates/my_template.html`](https://docs.djangoproject.com/en/stable/topics/templates/)

<!--html-header-start-->

In your **Django app**'s HTML template, you can now embed your ReactPy component using the `component` template tag. Within this tag, you will need to type in the dotted path to the component.

Additionally, you can pass in `args` and `kwargs` into your component function. After reading the code below, pay attention to how the function definition for `hello_world` (_from the previous example_) accepts a `recipient` argument.

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

Follow the links below to find out more about this project.

-   [Try ReactPy (Jupyter Notebook)](https://mybinder.org/v2/gh/reactive-python/reactpy-jupyter/main?urlpath=lab/tree/notebooks/introduction.ipynb)
-   [Documentation](https://reactive-python.github.io/reactpy-django)
-   [GitHub Discussions](https://github.com/reactive-python/reactpy-django/discussions)
-   [Discord](https://discord.gg/uNb5P4hA9X)
-   [Contributor Guide](https://reactive-python.github.io/reactpy-django/latest/about/code/)
-   [Code of Conduct](https://github.com/reactive-python/reactpy-django/blob/main/CODE_OF_CONDUCT.md)
