## Overview

<p class="intro" markdown>

We supply some pre-designed that components can be used to help simplify development.

</p>

---

## PyScript Component

This allows you to embedded any number of client-side PyScript components within traditional ReactPy components.

{% include-markdown "../reference/template-tag.md" start="<!--pyscript-def-start-->" end="<!--pyscript-def-end-->" %}

=== "components.py"

    ```python
    {% include "../../examples/python/pyscript-ssr-parent.py" %}
    ```

=== "root.py"

    ```python
    {% include "../../examples/python/pyscript-ssr-child.py" %}
    ```

=== "my_template.html"

    ```jinja
    {% include "../../examples/html/pyscript-ssr-parent.html" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python *file_paths` | `#!python str` | File path to your client-side component. If multiple paths are provided, the contents are automatically merged. | N/A |
    | `#!python initial` | `#!python str | VdomDict | ComponentType` | The initial HTML that is displayed prior to the PyScript component loads. This can either be a string containing raw HTML, a `#!python reactpy.html` snippet, or a non-interactive component. | `#!python ""` |
    | `#!python root` | `#!python str` | The name of the root component function. | `#!python "root"` |

<!--pyscript-setup-required-start-->

??? warning "You must call `pyscript_setup` in your Django template before using this tag!"

    This requires using of the [`#!jinja {% pyscript_setup %}` template tag](./template-tag.md#pyscript-setup) to initialize PyScript on the client.

    === "my_template.html"

        ```jinja
        {% include "../../examples/html/pyscript-setup.html" %}
        ```

<!--pyscript-setup-required-end-->

{% include-markdown "../reference/template-tag.md" start="<!--pyscript-js-exec-start-->" end="<!--pyscript-js-exec-end-->" %}

{% include-markdown "../reference/template-tag.md" start="<!--pyscript-multifile-start-->" end="<!--pyscript-multifile-end-->" trailing-newlines=false preserve-includer-indent=false %}

    === "components.py"

        ```python
        {% include "../../examples/python/pyscript-component-multiple-files-root.py" %}
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

    The value for `#!python initial` is most commonly be a `#!python reactpy.html` snippet or a non-interactive `#!python @component`.

    === "components.py"

        ```python
        {% include "../../examples/python/pyscript-component-initial-object.py" %}
        ```

    However, you can also use a string containing raw HTML.

    === "components.py"

        ```python
        {% include "../../examples/python/pyscript-component-initial-string.py" %}
        ```

??? question "Can I use a different name for my root component?"

    Yes, you can use the `#!python root` keyword to specify a different name for your root function.

    === "components.py"

        ```python
        {% include "../../examples/python/pyscript-component-root.py" %}
        ```

    === "main.py"

        ```python
        {% include "../../examples/python/pyscript-root.py" %}
        ```

---

## View To Component

Automatically convert a Django view into a component.

At this time, this works best with static views with no interactivity.

Compatible with sync or async [Function Based Views](https://docs.djangoproject.com/en/dev/topics/http/views/) and [Class Based Views](https://docs.djangoproject.com/en/dev/topics/class-based-views/).

=== "components.py"

    ```python
    {% include "../../examples/python/vtc.py" %}
    ```

=== "views.py"

    ```python
    {% include "../../examples/python/hello_world_fbv.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python view` | `#!python Callable | View | str` | The view to convert, or the view's dotted path as a string. | N/A |
    | `#!python transforms` | `#!python Sequence[Callable[[VdomDict], Any]]` | A list of functions that transforms the newly generated VDOM. The functions will be called on each VDOM node. | `#!python tuple` |
    | `#!python strict_parsing` | `#!python bool` | If `#!python True`, an exception will be generated if the HTML does not perfectly adhere to HTML5. | `#!python True` |

    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python constructor` | A function that takes `#!python request, *args, key, **kwargs` and returns a ReactPy component. Note that `#!python *args` and `#!python **kwargs` are directly provided to your view. |

??? info "Existing limitations"

    There are currently several limitations of using `#!python view_to_component` that may be resolved in a future version.

    - Requires manual intervention to change HTTP methods to anything other than `GET`.
    - ReactPy events cannot conveniently be attached to converted view HTML.
    - Has no option to automatically intercept local anchor link (such as `#!html <a href='example/'></a>`) click events.

??? question "How do I use this for Class Based Views?"

    Class Based Views are accepted by `#!python view_to_component` as an argument.

    Calling `#!python as_view()` is optional, but recommended.

    === "components.py"

        ```python
        {% include "../../examples/python/vtc-cbv.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_cbv.py" %}
        ```

??? question "How do I provide `#!python request`, `#!python args`, and `#!python kwargs` to a converted view?"

    This component accepts `#!python request`, `#!python *args`, and `#!python **kwargs` arguments, which are sent to your provided view.

    === "components.py"

        ```python
        {% include "../../examples/python/vtc-args.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_args_kwargs.py" %}
        ```

??? question "How do I customize this component's behavior?"

    This component accepts arguments that can be used to customize its behavior.

    Below are all the arguments that can be used.

    ---

    <font size="4">**`#!python strict_parsing`**</font>

    By default, an exception will be generated if your view's HTML does not perfectly adhere to HTML5.

    However, there are some circumstances where you may not have control over the original HTML, so you may be unable to fix it. Or you may be relying on non-standard HTML tags such as `#!html <my-tag> Hello World </my-tag>`.

    In these scenarios, you may want to rely on best-fit parsing by setting the `#!python strict_parsing` parameter to `#!python False`. This uses `libxml2` recovery algorithm, which is designed to be similar to how web browsers would attempt to parse non-standard or broken HTML.

    === "components.py"

        ```python
        {% include "../../examples/python/vtc-strict-parsing.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_fbv.py" %}
        ```

    ---

    <font size="4">**`#!python transforms`**</font>

    After your view has been turned into [VDOM](https://reactpy.dev/docs/reference/specifications.html#vdom) (python dictionaries), `#!python view_to_component` will call your `#!python transforms` functions on every VDOM node.

    This allows you to modify your view prior to rendering.

    For example, if you are trying to modify the text of a node with a certain `#!python id`, you can create a transform like such:

    === "components.py"

        ```python
        {% include "../../examples/python/vtc-transforms.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_fbv_with_id.py" %}
        ```

---

## View To Iframe

Automatically convert a Django view into an [`iframe` element](https://www.techtarget.com/whatis/definition/IFrame-Inline-Frame).

The contents of this `#!python iframe` is handled entirely by traditional Django view rendering. While this solution is compatible with more views than `#!python view_to_component`, it comes with different limitations.

Compatible with sync or async [Function Based Views](https://docs.djangoproject.com/en/dev/topics/http/views/) and [Class Based Views](https://docs.djangoproject.com/en/dev/topics/class-based-views/).

=== "components.py"

    ```python
    {% include "../../examples/python/vti.py" %}
    ```

=== "views.py"

    ```python
    {% include "../../examples/python/hello_world_fbv.py" %}
    ```

=== "apps.py"

    ```python
    {% include "../../examples/python/hello_world_app_config_fbv.py" %}
    ```

??? example "See Interface"

    <font size="4">**Parameters**</font>

    | Name | Type | Description | Default |
    | --- | --- | --- | --- |
    | `#!python view` | `#!python Callable | View | str` | The view function or class to convert. | N/A |
    | `#!python extra_props` | `#!python Mapping[str, Any] | None` | Additional properties to add to the `iframe` element. | `#!python None` |


    <font size="4">**Returns**</font>

    | Type | Description |
    | --- | --- |
    | `#!python constructor` | A function that takes `#!python *args, key, **kwargs` and returns a ReactPy component. Note that `#!python *args` and `#!python **kwargs` are directly provided to your view. |

??? info "Existing limitations"

    There are currently several limitations of using `#!python view_to_iframe` that may be resolved in a future version.

    - No built-in method of signalling events back to the parent component.
    - All provided `#!python *args` and `#!python *kwargs` must be serializable values, since they are encoded into the URL.
    - The `#!python iframe` will always load **after** the parent component.
    - CSS styling for `#!python iframe` elements tends to be awkward/difficult.

??? question "How do I use this for Class Based Views?"

    Class Based Views are accepted by `#!python view_to_iframe` as an argument.

    Calling `#!python as_view()` is optional, but recommended.

    === "components.py"

        ```python
        {% include "../../examples/python/vti-cbv.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_cbv.py" %}
        ```

    === "apps.py"

        ```python
        {% include "../../examples/python/hello_world_app_config_cbv.py" %}
        ```

??? question "How do I provide `#!python args` and `#!python kwargs` to a converted view?"

    This component accepts `#!python *args` and `#!python **kwargs` arguments, which are sent to your provided view.

    All provided `#!python *args` and `#!python *kwargs` must be serializable values, since they are encoded into the URL.

    === "components.py"

        ```python
        {% include "../../examples/python/vti-args.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_fbv.py" %}
        ```

    === "apps.py"

        ```python
        {% include "../../examples/python/hello_world_app_config_fbv.py" %}
        ```

??? question "How do I customize this component's behavior?"

    This component accepts arguments that can be used to customize its behavior.

    Below are all the arguments that can be used.

    ---

    <font size="4">**`#!python extra_props`**</font>

    This component accepts a `#!python extra_props` parameter, which is a dictionary of additional properties to add to the `#!python iframe` element.

    For example, if you want to add a `#!python title` attribute to the `#!python iframe` element, you can do so like such:

    === "components.py"

        ```python
        {% include "../../examples/python/vti-extra-props.py" %}
        ```

    === "views.py"

        ```python
        {% include "../../examples/python/hello_world_fbv.py" %}
        ```

    === "apps.py"

        ```python
        {% include "../../examples/python/hello_world_app_config_fbv.py" %}
        ```

---

## Django CSS

Allows you to defer loading a CSS stylesheet until a component begins rendering. This stylesheet must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

=== "components.py"

    ```python
    {% include "../../examples/python/django-css.py" %}
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
    {% include "../../examples/python/django-css-local-link.py" %}
    ```

??? question "How do I load external CSS?"

    `#!python django_css` can only be used with local static files.

    For external CSS, you should use `#!python html.link`.

    ```python
    {% include "../../examples/python/django-css-external-link.py" %}
    ```

??? question "Why not load my CSS in `#!html <head>`?"

    Traditionally, stylesheets are loaded in your `#!html <head>` using Django's `#!jinja {% static %}` template tag.

    However, to help improve webpage load times you can use this `#!python django_css` component to defer loading your stylesheet until it is needed.

---

## Django JS

Allows you to defer loading JavaScript until a component begins rendering. This JavaScript must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

<!--
TODO: This is no longer true since we don't insert elements on the page via JSON Patch anymore.
However, we may go back to diffing at some point in the future.

!!! warning "Pitfall"

Be mindful of load order! If your JavaScript relies on the component existing on the page, you must place `django_js` at the **bottom** of your component.
 -->

=== "components.py"

    ```python
    {% include "../../examples/python/django-js.py" %}
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
    {% include "../../examples/python/django-js-local-script.py" %}
    ```

??? question "How do I load external JS?"

    `#!python django_js` can only be used with local static files.

    For external JavaScript, you should use `#!python html.script`.

    ```python
    {% include "../../examples/python/django-js-remote-script.py" %}
    ```

??? question "Why not load my JS in `#!html <head>`?"

    Traditionally, JavaScript is loaded in your `#!html <head>` using Django's `#!jinja {% static %}` template tag.

    However, to help improve webpage load times you can use this `#!python django_js` component to defer loading your JavaScript until it is needed.
