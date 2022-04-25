???+ summary

       Use our template tag in your HTML.

---

{% include-markdown "../../README.md" start="<!--html-header-start-->" end="<!--html-header-end-->" %}

{% include-markdown "../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

{% include-markdown "../django/templatetag.md" start="<!--q-multiple-components-start-->" end="<!--q-multiple-components-end-->" %}

??? question "Can I use positional arguments instead of keyworded arguments?"

       You can only pass in **keyworded arguments** within the template tag. Due to technical limitations, **positional arguments** are not supported at this time.

       Also, be mindful of [reserved keywords](../django/templatetag.md).

??? question "Where is my templates folder?"

       If you do not have a `templates` folder in your **Django app**, you can simply create one! Keep in mind, templates within this folder will not be detected by Django unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).
