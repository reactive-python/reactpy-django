## Overview

<p class="intro" markdown>

We supply some pre-designed that components can be used to help simplify development.

</p>

---

## View To Component

Convert any Django view into a ReactPy component by using this decorator. Compatible with [Function Based Views](https://docs.djangoproject.com/en/dev/topics/http/views/) and [Class Based Views](https://docs.djangoproject.com/en/dev/topics/class-based-views/). Views can be sync or async.

=== "components.py"

    ```python
    {% include "../../python/vtc.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python view` | `#!python Callable | View` | The view function or class to convert. | N/A |
    | `#!python compatibility` | `#!python bool` | If `#!python True`, the component will be rendered in an iframe. When using compatibility mode `#!python tranforms`, `#!python strict_parsing`, `#!python request`, `#!python args`, and `#!python kwargs` arguments will be ignored. | `#!python False` |
    | `#!python transforms` | `#!python Sequence[Callable[[VdomDict], Any]]` | A list of functions that transforms the newly generated VDOM. The functions will be called on each VDOM node. | `#!python tuple` |
    | `#!python strict_parsing` | `#!python bool` | If `#!python True`, an exception will be generated if the HTML does not perfectly adhere to HTML5. | `#!python True` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python _ViewComponentConstructor` | A function that takes `#!python request, *args, key, **kwargs` and returns a ReactPy component. All parameters are directly provided to your view, besides `#!python key` which is used by ReactPy. |

??? Warning "Potential information exposure when using `#!python compatibility = True`"

    When using `#!python compatibility` mode, ReactPy automatically exposes a URL to your view.

    It is your responsibility to ensure privileged information is not leaked via this method.

    You must implement a method to ensure only authorized users can access your view. This can be done via directly writing conditionals into your view, or by adding decorators such as [`#!python user_passes_test`](https://docs.djangoproject.com/en/dev/topics/auth/default/#django.contrib.auth.decorators.user_passes_test) to your views. For example...

    === "Function Based View"

        ```python
        {% include "../../python/vtc-fbv-compat.py" %}
        ```

    === "Class Based View"

        ```python
        {% include "../../python/vtc-cbv-compatibility.py" %}
        ```

??? info "Existing limitations"

    There are currently several limitations of using `#!python view_to_component` that may be resolved in a future version.

    - Requires manual intervention to change request methods beyond `GET`.
    - ReactPy events cannot conveniently be attached to converted view HTML.
    - Has no option to automatically intercept local anchor link (such as `#!html <a href='example/'></a>`) click events.

    _Please note these limitations do not exist when using `#!python compatibility` mode._

??? question "How do I use this for Class Based Views?"

    You can simply pass your Class Based View directly into `#!python view_to_component`.

    === "components.py"

        ```python
        {% include "../../python/vtc-cbv.py" %}
        ```

??? question "How do I transform views from external libraries?"

    In order to convert external views, you can utilize `#!python view_to_component` as a function, rather than a decorator.

    === "components.py"

        ```python
        {% include "../../python/vtc-func.py" %}
        ```

??? question "How do I provide `#!python request`, `#!python args`, and `#!python kwargs` to a view?"

    <font size="4">**`#!python Request`**</font>

    You can use the `#!python request` parameter to provide the view a custom request object.

    === "components.py"

        ```python
        {% include "../../python/vtc-request.py" %}
        ```

    ---

    <font size="4">**`#!python args` and `#!python kwargs`**</font>

    You can use the `#!python args` and `#!python kwargs` parameters to provide positional and keyworded arguments to a view.

    === "components.py"

        ```python
        {% include "../../python/vtc-args-kwargs.py" %}
        ```

??? question "How do I use `#!python strict_parsing`, `#!python compatibility`, and `#!python transforms`?"

    <font size="4">**`#!python strict_parsing`**</font>

    By default, an exception will be generated if your view's HTML does not perfectly adhere to HTML5.

    However, there are some circumstances where you may not have control over the original HTML, so you may be unable to fix it. Or you may be relying on non-standard HTML tags such as `#!html <my-tag> Hello World </my-tag>`.

    In these scenarios, you may want to rely on best-fit parsing by setting the `#!python strict_parsing` parameter to `#!python False`.

    === "components.py"

        ```python
        {% include "../../python/vtc-strict-parsing.py" %}
        ```

    _Note: Best-fit parsing is designed to be similar to how web browsers would handle non-standard or broken HTML._

    ---

    <font size="4">**`#!python compatibility`**</font>

    For views that rely on HTTP responses other than `GET` (such as `PUT`, `POST`, `PATCH`, etc), you should consider using compatibility mode to render your view within an iframe.

    Any view can be rendered within compatibility mode. However, the `#!python transforms`, `#!python strict_parsing`, `#!python request`, `#!python args`, and `#!python kwargs` arguments do not apply to compatibility mode.



    === "components.py"

        ```python
        {% include "../../python/vtc-compatibility.py" %}
        ```

    _Note: By default the `#!python compatibility` iframe is unstyled, and thus won't look pretty until you add some CSS._

    ---

    <font size="4">**`#!python transforms`**</font>

    After your view has been turned into [VDOM](https://reactpy.dev/docs/reference/specifications.html#vdom) (python dictionaries), `#!python view_to_component` will call your `#!python transforms` functions on every VDOM node.

    This allows you to modify your view prior to rendering.

    For example, if you are trying to modify the text of a node with a certain `#!python id`, you can create a transform like such:

    === "components.py"

        ```python
        {% include "../../python/vtc-transforms.py" %}
        ```

## Django CSS

Allows you to defer loading a CSS stylesheet until a component begins rendering. This stylesheet must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

=== "components.py"

    ```python
    {% include "../../python/django-css.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python static_path` | `#!python str` | The path to the static file. This path is identical to what you would use on Django's `#!jinja {% static %}` template tag. | N/A |
    | `#!python key` | `#!python Key | None` | A key to uniquely identify this component which is unique amongst a component's immediate siblings | `#!python None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Component` | A ReactPy component. |

??? question "Can I load static CSS using `#!python html.link` instead?"

    While you can load stylesheets with `#!python html.link`, keep in mind that loading this way **does not** ensure load order. Thus, your stylesheet will be loaded after your component is displayed. This would likely cause unintended visual behavior, so use this at your own discretion.

    Here's an example on what you should avoid doing for Django static files:

    ```python
    {% include "../../python/django-css-local-link.py" %}
    ```

??? question "How do I load external CSS?"

    `#!python django_css` can only be used with local static files.

    For external CSS, you should use `#!python html.link`.

    ```python
    {% include "../../python/django-css-external-link.py" %}
    ```

??? question "Why not load my CSS in `#!html <head>`?"

    Traditionally, stylesheets are loaded in your `#!html <head>` using Django's `#!jinja {% static %}` template tag.

    However, to help improve webpage load times you can use this `#!python django_css` component to defer loading your stylesheet until it is needed.

## Django JS

Allows you to defer loading JavaScript until a component begins rendering. This JavaScript must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

!!! warning "Pitfall"

    Be mindful of load order! If your JavaScript relies on the component existing on the page, you must place `django_js` at the **bottom** of your component.

=== "components.py"

    ```python
    {% include "../../python/django-js.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python static_path` | `#!python str` | The path to the static file. This path is identical to what you would use on Django's `#!jinja {% static %}` template tag. | N/A |
    | `#!python key` | `#!python Key | None` | A key to uniquely identify this component which is unique amongst a component's immediate siblings | `#!python None` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python Component` | A ReactPy component. |

??? question "Can I load static JavaScript using `#!python html.script` instead?"

    While you can load JavaScript with `#!python html.script`, keep in mind that loading this way **does not** ensure load order. Thus, your JavaScript will likely be loaded at an arbitrary time after your component is displayed.

    Here's an example on what you should avoid doing for Django static files:

    ```python
    {% include "../../python/django-js-local-script.py" %}
    ```

??? question "How do I load external JS?"

    `#!python django_js` can only be used with local static files.

    For external JavaScript, you should use `#!python html.script`.

    ```python
    {% include "../../python/django-js-remote-script.py" %}
    ```

??? question "Why not load my JS in `#!html <head>`?"

    Traditionally, JavaScript is loaded in your `#!html <head>` using Django's `#!jinja {% static %}` template tag.

    However, to help improve webpage load times you can use this `#!python django_js` component to defer loading your JavaScript until it is needed.
