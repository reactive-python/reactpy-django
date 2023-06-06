## Overview

!!! summary "Overview"

      Create a component function using our decorator.

## Create a Component

{% include-markdown "../../../README.md" start="<!--py-header-start-->" end="<!--py-header-end-->" %}

=== "components.py"

      {% include-markdown "../../../README.md" start="<!--py-code-start-->" end="<!--py-code-end-->" %}

??? question "What should I name my ReactPy files and functions?"

      You have full freedom in naming/placement of your files and functions.

      We recommend creating a `components.py` for small **Django apps**. If your app has a lot of components, you should consider breaking them apart into individual modules such as `components/navbar.py`.

      Ultimately, components are referenced by Python dotted path in `my-template.html` (_see next step_). So, at minimum this path needs to be valid to Python's `importlib`.
