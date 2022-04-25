{% include-markdown "../../README.md" start="<!--py-header-start-->" end="<!--py-header-end-->" %}

{% include-markdown "../../README.md" start="<!--py-code-start-->" end="<!--py-code-end-->" %}

!!! note "Note: File Naming"

      You can name `components.py` anything you wish, and place it within any Python module.

      You should determine the best way to sort your Python modules and component functions to fit your needs.

      Ultimately, components are referenced by Python dotted path in `my-template.html`. So, at minimum this path needs to be valid to Python's `importlib`.
