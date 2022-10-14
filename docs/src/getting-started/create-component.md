???+ summary

      Create a component function using our decorator.

---

{% include-markdown "../../../README.md" start="<!--py-header-start-->" end="<!--py-header-end-->" %}

=== "components.py"

      {% include-markdown "../../../README.md" start="<!--py-code-start-->" end="<!--py-code-end-->" %}

??? question "What should I name my IDOM files and functions?"

      You have full freedom in naming/placement of your files and functions.

      You should determine the best way to sort your Python modules and component functions to fit your needs.

      Ultimately, components are referenced by Python dotted path in `my-template.html` (_see next step_). So, at minimum this path needs to be valid to Python's `importlib`.
