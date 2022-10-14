???+ summary

    Prefabricated components can be used within your `components.py` to help simplify development.

## View To Component

Convert any Django view into a IDOM component by usng this decorator. Compatible with sync/async [Function Based Views](https://docs.djangoproject.com/en/dev/topics/http/views/) and [Class Based Views](https://docs.djangoproject.com/en/dev/topics/class-based-views/).

=== "components.py"

    ```python linenums="1"
    from idom import component, html
    from django.http import HttpResponse
    from django_idom.components import view_to_component

    @view_to_component
    def hello_world_view(request):
        return HttpResponse("Hello World!")

    @component
    def my_component():
        return html.div(
            hello_world_view(),
        )
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | view | `Callable | View` | The view function or class to convert. | N/A |
    | compatibility | `bool` | If True, the component will be rendered in an iframe. When using compatibility mode `tranforms`, `strict_parsing`, `request`, `args`, and `kwargs` arguments will be ignored. | `False` |
    | transforms | `Sequence[Callable[[VdomDict], Any]]` | A list of functions that transforms the newly generated VDOM. The functions will be called on each VDOM node. | `tuple` |
    | strict_parsing | `bool` | If True, an exception will be generated if the HTML does not perfectly adhere to HTML5. | `True` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `_ViewComponentConstructor` | A function that takes `request: HttpRequest | None, *args: Any, **kwargs: Any` and returns an IDOM component. |

??? warning "Existing limitations"

    There are currently several limitations of using `view_to_component` that may be resolved in a future version of `django_idom`.

    - Requires manual intervention to change request methods beyond `GET`.
    - Does not currently load any HTML contained with a `<head>` tag
    - Has no option to automatically intercept local anchor link (ex. `#!html <a href='example/'></a>`) click events

    _Please note these limitations do not exist when using `compatibility` mode._

??? question "How do I use this for Class Based Views?"

    You can simply pass your Class Based View directly into `view_to_component`.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse
        from django.views import View
        from django_idom.components import view_to_component

        @view_to_component
        class HelloWorldView(View):
            def get(self, request):
                return HttpResponse("Hello World!")

        @component
        def my_component():
            return html.div(
                HelloWorldView(),
            )
        ```

??? question "How do I transform views from external libraries?"

    === "components.py"

        In order to convert external views, you can utilize `view_to_component` as a function, rather than a decorator.

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse
        from django_idom.components import view_to_component
        from some_library.views import example_view

        converted_view = view_to_component(example_view)

        @component
        def my_component():
            return html.div(
                converted_view(),
            )
        ```

??? question "How do I provide `args` and `kwargs` to a view?"

    You can use the `args` and `kwargs` parameters to provide positional and keyworded arguments to a view.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse
        from django_idom.components import view_to_component

        @view_to_component
        def hello_world_view(request, arg1, arg2, key1=None, key2=None):
            return HttpResponse(f"Hello World! {arg1} {arg2} {key1} {key2}")

        @component
        def my_component():
            return html.div(
                hello_world_view(
                    None, # Your request object (optional)
                    "value_1",
                    "value_2",
                    key1="abc",
                    key2="123",
                ),
            )
        ```

??? question "How do I provide a custom `request` object to a view?"

    You can use the `request` parameter to provide the view a custom request object.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse, HttpRequest
        from django_idom.components import view_to_component

        example_request = HttpRequest()
        example_request.method = "PUT"

        @view_to_component
        def hello_world_view(request):
            return HttpResponse(f"Hello World! {request.method}")

        @component
        def my_component():
            return html.div(
                hello_world_view(
                    example_request,
                ),
            )
        ```

??? question "What is `compatibility` mode?"

    For views that rely on HTTP responses other than `GET` (such as `PUT`, `POST`, `PATCH`, etc), you should consider using compatibility mode to render your view within an iframe.

    Any view can be rendered within compatibility mode. However, the `transforms`, `strict_parsing`, `request`, `args`, and `kwargs` arguments do not apply to compatibility mode.

    Please note that by default the iframe is unstyled, and thus won't look pretty until you add some CSS.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse
        from django_idom.components import view_to_component

        @view_to_component(compatibility=True)
        def hello_world_view(request):
            return HttpResponse("Hello World!")

        @component
        def my_component():
            return html.div(
                hello_world_view(),
            )
        ```

??? question "What is `strict_parsing`?"

    By default, an exception will be generated if your view's HTML does not perfectly adhere to HTML5.

    However, there are some circumstances where you may not have control over the original HTML, so you may be unable to fix it. Or you may be relying on non-standard HTML tags such as `#!html <my-tag> Hello World </my-tag>`.

    In these scenarios, you may want to rely on best-fit parsing by setting the `strict_parsing` parameter to `False`.

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse
        from django_idom.components import view_to_component

        @view_to_component(strict_parsing=False)
        def hello_world_view(request):
            return HttpResponse("<my-tag> Hello World </my-tag>")

        @component
        def my_component():
            return html.div(
                hello_world_view(),
            )
        ```

    Note that best-fit parsing is very similar to how web browsers will handle broken HTML.

??? question "What is `transforms`?"

    After your view has been turned into [VDOM](https://idom-docs.herokuapp.com/docs/reference/specifications.html#vdom) (python dictionaries), `view_to_component` will call your `transforms` functions on every VDOM node.

    This allows you to modify your view prior to rendering.

    For example, if you are trying to modify the text of a node with a certain `id`, you can create a transform like such:

    === "components.py"

        ```python linenums="1"
        from idom import component, html
        from django.http import HttpResponse
        from django_idom.components import view_to_component

        def example_transform(vdom):
            attributes = vdom.get("attributes")
            if attributes and attributes.get("id") == "hello-world":
                vdom["children"][0] = "Good Bye World!"

        @view_to_component(transforms=[example_transform])
        def hello_world_view(request):
            return HttpResponse("<div id='hello-world'> Hello World! <div>")

        @component
        def my_component():
            return html.div(
                hello_world_view(),
            )
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
