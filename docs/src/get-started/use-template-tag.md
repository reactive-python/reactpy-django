## Overview

!!! summary "Overview"

       Decide where the component will be displayed by using our template tag.

## Use the Template Tag

{% include-markdown "../../../README.md" start="<!--html-header-start-->" end="<!--html-header-end-->" %}

=== "my-template.html"

       {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

{% include-markdown "../features/template-tag.md" start="<!--context-start-->" end="<!--context-end-->" %}

{% include-markdown "../features/template-tag.md" start="<!--reserved-arg-start-->" end="<!--reserved-arg-end-->" %}

{% include-markdown "../features/template-tag.md" start="<!--multiple-components-start-->" end="<!--multiple-components-end-->" %}

??? question "Where is my templates folder?"

       If you do not have a `templates` folder in your **Django app**, you can simply create one! Keep in mind, templates within this folder will not be detected by Django unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).
