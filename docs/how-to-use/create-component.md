???+ summary

      Create a component function using our decorator.

---

{% include-markdown "../../README.md" start="<!--py-header-start-->" end="<!--py-header-end-->" %}

{% include-markdown "../../README.md" start="<!--py-code-start-->" end="<!--py-code-end-->" %}

??? question "What do I name my component files and functions?"

      You can have full freedom in where you name or place your files/functions within IDOM.

      You should determine the best way to sort your Python modules and component functions to fit your needs.

      Ultimately, components are referenced by Python dotted path in `my-template.html`. So, at minimum this path needs to be valid to Python's `importlib`.
