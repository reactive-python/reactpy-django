## Overview

<p class="intro" markdown>

Decide where the component will be displayed by using our template tag.

</p>

---

## Embedding a component in a template

{% include-markdown "../../../README.md" start="<!--html-header-start-->" end="<!--html-header-end-->" %}

Additionally, you can pass in `args` and `kwargs` into your component function. After reading the code below, pay attention to how the function definition for `hello_world` ([_from the previous step_](./create-component.md)) accepts a `recipient` argument.

=== "my-template.html"

       {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

{% include-markdown "../features/template-tag.md" start="<!--context-start-->" end="<!--context-end-->" %}

{% include-markdown "../features/template-tag.md" start="<!--multiple-components-start-->" end="<!--multiple-components-end-->" %}

??? question "Where is my templates folder?"

       If you do not have a `templates` folder in your **Django app**, you can simply create one! Keep in mind, templates within this folder will not be detected by Django unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).
