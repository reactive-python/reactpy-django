## Overview

<p class="intro" markdown>

We supply some pre-generated that HTML nodes can be used to help simplify development.

</p>

---

## PyScript

PyScript code block. The text content of this tag are executed within the PyScript interpreter. This can be used as an alternative to the `#!python reactpy.html.script`.

This is a primitive HTML tag that is leveraged by [`reactpy_django.components.pyscript_component`](./components.md#pyscript-component).

The `pyscript` tag functions identically to HTML tags contained within `#!python reactpy.html`.

=== "components.py"

    ```python
    {% include "../../examples/python/pyscript-tag.py" %}
    ```

=== "my_template.html"

    ```jinja
    {% include "../../examples/html/pyscript-tag.html" %}
    ```

{% include-markdown "../reference/components.md" start="<!--pyscript-setup-required-start-->" end="<!--pyscript-setup-required-end-->" %}
