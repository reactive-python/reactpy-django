## Overview

<p class="intro" markdown>

We supply some pre-generated that HTML nodes can be used to help simplify development.

</p>

---

## PyScript

Primitive HTML tag that is leveraged by [`reactpy_django.components.pyscript_component`](./components.md#pyscript-component).

This can be used as an alternative to the `#!python reactpy.html.script` tag to execute JavaScript and run client-side Python code.

Additionally, this tag functions identically to any other tag contained within `#!python reactpy.html`, and can be used in the same way.

=== "components.py"

    ```python
    {% include "../../examples/python/pyscript-tag.py" %}
    ```

=== "my_template.html"

    ```jinja
    {% include "../../examples/html/pyscript-tag.html" %}
    ```

{% include-markdown "../reference/components.md" start="<!--pyscript-setup-required-start-->" end="<!--pyscript-setup-required-end-->" %}
