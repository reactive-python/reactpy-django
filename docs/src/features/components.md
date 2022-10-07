???+ summary

    Prefabricated components can be used within your `components.py` to help simplify development.

## View To Component

Convert any Django view into a IDOM component by usng this decorator. Compatible with sync/async [Function Based Views](https://docs.djangoproject.com/en/dev/topics/http/views/) and [Class Based Views](https://docs.djangoproject.com/en/dev/topics/class-based-views/).

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.components import view_to_component
    from .views import hello_world_view

    @component
    def my_component():
        return html.div(
            view_to_component(hello_world_view),
        )
    ```

=== "views.py"

    {% include-markdown "../../includes/examples.md" start="<!--hello-world-view-start-->" end="<!--hello-world-view-end-->" %}

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | view | `Callable | View` | The view function or class to convert. | N/A |
    | compatibility | `bool` | If True, the component will be rendered in an iframe. When using compatibility mode `tranforms`, `strict_parsing`, and `request` arguments will be ignored. | `False` |
    | transforms | `Iterable[Callable[[VdomDict], Any]]` | A list of functions that transforms the newly generated VDOM. The functions will be called on each VDOM node. | `tuple` |
    | strict_parsing | `bool` | If True, an exception will be generated if the HTML does not perfectly adhere to HTML5. | `True` |
    | request | `HttpRequest | None` | Request object to provide to the view. | `None` |
    | args | `Iterable` | The positional arguments to pass to the view. | `tuple` |
    | kwargs | `Dict | None` | The keyword arguments to pass to the view. | `None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |
    | `None` | No component render. |

??? question "How do I use this for Class Based Views?"

    You can simply pass your Class Based View directly into this function.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django_idom.components import view_to_component
        from .views import HelloWorldView

        @component
        def my_component():
            return html.div(
                view_to_component(HelloWorldView),
            )
        ```

    === "views.py"

        {% include-markdown "../../includes/examples.md" start="<!--hello-world-cbv-start-->" end="<!--hello-world-cbv-end-->" %}

??? question "How do I pass arguments into the view?"

    You can use the `args` and `kwargs` parameters to pass arguments to the view.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django_idom.components import view_to_component
        from .views import hello_world_view

        @component
        def my_component():
            return html.div(
                view_to_component(
                    hello_world_view,
                    args=["value_1", "value_2"],
                    kwargs={"key_1": "value_1", "key_2": "value_2"},
                ),
            )
        ```

    === "views.py"

        {% include-markdown "../../includes/examples.md" start="<!--hello-world-view-start-->" end="<!--hello-world-view-end-->" %}

??? question "What is `compatibility` mode?"

    For views that rely on HTTP responses other than `GET` (such as `PUT`, `POST`, `PATCH`, etc), you should consider using compatibility mode to render your view within an iframe.

    Any view can be rendered within compatibility mode. However, the `transforms`, `strict_parsing`, and `request` arguments do not apply to compatibility mode.

    Please note that by default the iframe is unstyled, and thus won't look pretty until you add some CSS.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django_idom.components import view_to_component
        from .views import hello_world_view

        @component
        def my_component():
            return html.div(
                view_to_component(hello_world_view, compatibility=True),
            )
        ```

    === "views.py"

        {% include-markdown "../../includes/examples.md" start="<!--hello-world-view-start-->" end="<!--hello-world-view-end-->" %}

??? question "What is `strict_parsing`?"

    By default, an exception will be generated if your view's HTML does not perfectly adhere to HTML5.

    However, there are some circumstances where you may not have control over the original HTML, so you may be unable to fix it. Or you may be relying on non-standard HTML tags such as `#!html <my-tag> Hello World </my-tag>`.

    In these scenarios, you may want to rely on best-fit parsing by setting the `strict_parsing` parameter to `False`.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django_idom.components import view_to_component
        from .views import hello_world_view

        @component
        def my_component():
            return html.div(
                view_to_component(hello_world_view, strict_parsing=False),
            )
        ```

    === "views.py"

        {% include-markdown "../../includes/examples.md" start="<!--hello-world-view-start-->" end="<!--hello-world-view-end-->" %}

    Note that best-fit parsing is very similar to how web browsers will handle broken HTML.

??? question "What is `transforms`?"

    After your view has been turned into [VDOM](https://idom-docs.herokuapp.com/docs/reference/specifications.html#vdom) (python dictionaries), `view_to_component` will call your `transforms` functions on every VDOM node.

    This allows you to modify your view prior to rendering.

    For example, if you are trying to modify the text of a node with a certain `id`, you can create a transform like such:

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django_idom.components import view_to_component
        from .views import hello_world_view

        def example_transform(vdom):
            attributes = vdom.get("attributes")

            if attributes and attributes.get("id") == "hello-world":
                vdom["children"][0] = "Good Bye World!"

        @component
        def my_component():
            return view_to_component(
                hello_world_view,
                transforms=[example_transform],
            )
        ```

    === "views.py"

        ```python linenums="1"
        from django.http import HttpResponse

        def hello_world_view(request, *args, **kwargs):
            return HttpResponse("<div id='hello-world'> Hello World! <div>")
        ```

## Django CSS

Allows you to defer loading a CSS stylesheet until a component begins rendering. This stylesheet must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.components import django_css

    @component
    def my_component():
        return html.div(
            django_css("css/buttons.css"),
            html.button("My Button!"),
        )
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | static_path | `str` | The path to the static file. This path is identical to what you would use on a `static` template tag. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |

??? question "Should I put `django_css` at the top of my component?"

    Yes, if the stylesheet contains styling for your component.

??? question "Can I load static CSS using `html.link` instead?"

    While you can load stylesheets with `html.link`, keep in mind that loading this way **does not** ensure load order. Thus, your stylesheet will be loaded after your component is displayed. This would likely cause some visual jankiness, so use this at your own discretion.

    Here's an example on what you should avoid doing for Django static files:

    ```python linenums="1"
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

    ```python linenums="1"
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

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django_idom.components import django_js

    @component
    def my_component():
        return html.div(
            html.button("My Button!"),
            django_js("js/scripts.js"),
        )
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | static_path | `str` | The path to the static file. This path is identical to what you would use on a `static` template tag. | N/A |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `Component` | An IDOM component. |

??? question "Should I put `django_js` at the bottom of my component?"

    Yes, if your scripts are reliant on the contents of the component.

??? question "Can I load static JavaScript using `html.script` instead?"

    While you can load JavaScript with `html.script`, keep in mind that loading this way **does not** ensure load order. Thus, your JavaScript will likely be loaded at an arbitrary time after your component is displayed.

    Here's an example on what you should avoid doing for Django static files:

    ```python linenums="1"
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

    ```python linenums="1"
    from idom import component, html

    @component
    def my_component():
        return html.div(
            html.script({"src": "https://example.com/external-scripts.js"}),
            html.button("My Button!"),
        )
    ```

??? question "Why not load my JS in `#!html <head>`?"

    Traditionally, JavaScript is loaded in your `#!html <head>` using the `#!jinja {% load static %}` template tag.

    To help improve webpage load times, you can use the `django_js` component to defer loading your JavaScript until it is needed.
