???+ summary

       Decide where the component will be displayed by using our template tag.

---

{% include-markdown "../../../README.md" start="<!--html-header-start-->" end="<!--html-header-end-->" %}

=== "my-template.html"

       {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

{% include-markdown "../features/templatetag.md" start="<!--context-start-->" end="<!--context-end-->" %}

{% include-markdown "../features/templatetag.md" start="<!--kwarg-start-->" end="<!--kwarg-end-->" %}

{% include-markdown "../features/templatetag.md" start="<!--multiple-components-start-->" end="<!--multiple-components-end-->" %}

??? question "Where is my templates folder?"

       If you do not have a `templates` folder in your **Django app**, you can simply create one! Keep in mind, templates within this folder will not be detected by Django unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).
