{% include-markdown "../../README.md" start="<!--html-header-start-->" end="<!--html-header-end-->" %}

{% include-markdown "../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

!!! note "Note: Keyworded Arguments"

        You can only pass in **keyworded arguments** within the template tag. Due to technical limitations, **positional arguments** are not supported at this time.

        Also, be mindful of [reserved keywords](../django/templatetag.md).

!!! note "Note: Django HTML Templates"

        If you do not have a `templates` folder in your **Django app**, you can simply create one! Keep in mind, templates within this folder will not be detected by Django unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).
