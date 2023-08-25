## Overview

<p class="intro" markdown>

You can let ReactPy know what functions are components by using the `#!python @component` decorator.

</p>

---

## Declaring a function as a root component

You will need a file to start creating ReactPy components.

We recommend creating a `components.py` file within your chosen **Django app** to start out. For this example, the file path will look like this: `./example_project/my_app/components.py`.

Within this file, you can define your component functions and then add ReactPy's `#!python @component` decorator.

=== "components.py"

      {% include-markdown "../../../README.md" start="<!--py-code-start-->" end="<!--py-code-end-->" %}

??? question "What should I name my ReactPy files and functions?"

      You have full freedom in naming/placement of your files and functions.

      We recommend creating a `components.py` for small **Django apps**. If your app has a lot of components, you should consider breaking them apart into individual modules such as `components/navbar.py`.

      Ultimately, components are referenced by Python dotted path in `my-template.html` ([_see next step_](./use-template-tag.md)). So, at minimum your component path needs to be valid to Python's `importlib`.

??? question "What does the decorator actually do?"

      While not all components need to be decorated, there are a few features this decorator adds to your components.

      1. The ability to be used as a root component.
          - The decorator is required for any component that you want to reference in your Django templates ([_see next step_](./use-template-tag.md)).
      2. The ability to use [hooks](../features/hooks.md).
          - The decorator is required on any component where hooks are defined.
      3. Scoped failures.
          - If a decorated component generates an exception, then only that one component will fail to render.
