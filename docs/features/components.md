## Django CSS

Allows you to defer loading a CSS stylesheet until a component begins rendering. This stylesheet must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

```python title="components.py"
from idom import component, html
from django_idom.components import django_css

@component
def my_component():
    return html.div(
        django_css("css/buttons.css"),
        html.button("My Button!"),
    )
```

??? question "Should I put `django_css` at the top of my component?"

    Yes, if the stylesheet contains styling for your component.

??? question "Can I load static CSS using `html.link` instead?"

    While you can load stylesheets with `html.link`, keep in mind that loading this way **does not** ensure load order. Thus, your stylesheet will be loaded after your component is displayed. This would likely cause some visual jankiness, so use this at your own discretion.

    Here's an example on what you should avoid doing for Django static files:

    ```python
    from idom import component, html
    from django.templatetags.static import static

    @component
    def my_component():
        return html.div(
            html.link({"rel": "stylesheet", "href": static("css/buttons.css")}),
            html.button("My Button!"),
        )
    ```

??? question "How do I load external CSS?"

    `django_css` can only be used with local static files.

    For external CSS, substitute `django_css` with `html.link`.

    ```python
    from idom import component, html

    @component
    def my_component():
        return html.div(
            html.link({"rel": "stylesheet", "href": "https://example.com/external-styles.css"}),
            html.button("My Button!"),
        )
    ```

??? question "Why not load my CSS in `#!html <head>`?"

    Traditionally, stylesheets are loaded in your `#!html <head>` using the `#!jinja {% load static %}` template tag.

    To help improve webpage load times, you can use the `django_css` component to defer loading your stylesheet until it is needed.

## Django JS

Allows you to defer loading JavaScript until a component begins rendering. This JavaScript must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

```python title="components.py"
from idom import component, html
from django_idom.components import django_js

@component
def my_component():
    return html.div(
        html.button("My Button!"),
        django_js("js/scripts.js"),
    )
```

??? question "Should I put `django_js` at the bottom of my component?"

    Yes, if your scripts are reliant on the contents of the component.

??? question "Can I load static JavaScript using `html.script` instead?"

    While you can load JavaScript with `html.script`, keep in mind that loading this way **does not** ensure load order. Thus, your JavaScript will likely be loaded at an arbitrary time after your component is displayed.

    Here's an example on what you should avoid doing for Django static files:

    ```python
    from idom import component, html
    from django.templatetags.static import static

    @component
    def my_component():
        return html.div(
            html.script({"src": static("js/scripts.js")}),
            html.button("My Button!"),
        )
    ```

??? question "How do I load external JS?"

    `django_js` can only be used with local static files.

    For external JavaScript, substitute `django_js` with `html.script`.

    ```python
    from idom import component, html

    @component
    def my_component():
        return html.div(
            html.script({"src": static("https://example.com/external-scripts.js")}),
            html.button("My Button!"),
        )
    ```

??? question "Why not load my JS in `#!html <head>`?"

    Traditionally, JavaScript is loaded in your `#!html <head>` using the `#!jinja {% load static %}` template tag.

    To help improve webpage load times, you can use the `django_js` component to defer loading your JavaScript until it is needed.
