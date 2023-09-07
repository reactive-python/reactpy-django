## Overview

<p class="intro" markdown>

Components are one of the core concepts of ReactPy. They are the foundation upon which you build user interfaces (UI), which makes them the perfect place to start your journey!

</p>

!!! note

    If you have reached this point, you should have already [installed ReactPy-Django](../learn/add-reactpy-to-a-django-project.md) through the previous steps.

---

## Selecting a Django App

You will now need to pick at least one **Django app** to start using ReactPy-Django on.

For the following examples, we will assume the following:

1. You have a **Django app** named `my_app`, which was created by Django's [`startapp` command](https://docs.djangoproject.com/en/dev/intro/tutorial01/#creating-the-polls-app).
2. You have placed `my_app` directly into your **Django project** folder (`./example_project/my_app`). This is common for small projects.

??? question "How do I organize my Django project for ReactPy?"

      ReactPy-Django has no project structure requirements. Organize everything as you wish, just like any **Django project**.

## Defining a component

You will need a file to start creating ReactPy components.

We recommend creating a `components.py` file within your chosen **Django app** to start out. For this example, the file path will look like this: `./example_project/my_app/components.py`.

Within this file, you can define your component functions using ReactPy's `#!python @component` decorator.

=== "components.py"

      {% include-markdown "../../../README.md" start="<!--py-code-start-->" end="<!--py-code-end-->" %}

??? question "What should I name my ReactPy files and functions?"

      You have full freedom in naming/placement of your files and functions.

      We recommend creating a `components.py` for small **Django apps**. If your app has a lot of components, you should consider breaking them apart into individual modules such as `components/navbar.py`.

      Ultimately, components are referenced by Python dotted path in `my-template.html` ([_see next step_](#embedding-in-a-template)). This path must be valid to Python's `#!python importlib`.

??? question "What does the decorator actually do?"

      While not all components need to be decorated, there are a few features this decorator adds to your components.

      1. The ability to be used as a root component.
          - The decorator is required for any component that you want to reference in your Django templates ([_see next step_](#embedding-in-a-template)).
      2. The ability to use [hooks](../reference/hooks.md).
          - The decorator is required on any component where hooks are defined.
      3. Scoped failures.
          - If a decorated component generates an exception, then only that one component will fail to render.

## Embedding in a template

In your **Django app**'s HTML template, you can now embed your ReactPy component using the `#!jinja {% component %}` template tag. Within this tag, you will need to type in the dotted path to the component.

Additionally, you can pass in `#!python args` and `#!python kwargs` into your component function. After reading the code below, pay attention to how the function definition for `#!python hello_world` ([_from the previous step_](#defining-a-component)) accepts a `#!python recipient` argument.

=== "my-template.html"

       {% include-markdown "../../../README.md" start="<!--html-code-start-->" end="<!--html-code-end-->" %}

{% include-markdown "../reference/template-tag.md" start="<!--context-start-->" end="<!--context-end-->" %}

{% include-markdown "../reference/template-tag.md" start="<!--multiple-components-start-->" end="<!--multiple-components-end-->" %}

??? question "Where is my templates folder?"

       If you do not have a `./templates/` folder in your **Django app**, you can simply create one! Keep in mind, templates within this folder will not be detected by Django unless you [add the corresponding **Django app** to `settings.py:INSTALLED_APPS`](https://docs.djangoproject.com/en/dev/ref/applications/#configuring-applications).

## Setting up a Django view

Within your **Django app**'s `views.py` file, you will need to [create a view function](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) to render the HTML template `my-template.html` ([_from the previous step_](#embedding-in-a-template)).

=== "views.py"

    ```python
    {% include "../../python/example/views.py" %}
    ```

We will add this new view into your [`urls.py`](https://docs.djangoproject.com/en/dev/intro/tutorial01/#write-your-first-view) and define what URL it should be accessible at.

=== "urls.py"

    ```python
    {% include "../../python/example/urls.py" %}
    ```

??? question "Which urls.py do I add my views to?"

    For simple **Django projects**, you can easily add all of your views directly into the **Django project's** `urls.py`. However, as you start increase your project's complexity you might end up with way too much within one file.

    Once you reach that point, we recommend creating an individual `urls.py` within each of your **Django apps**.

    Then, within your **Django project's** `urls.py` you will use Django's [`include` function](https://docs.djangoproject.com/en/dev/ref/urls/#include) to link it all together.

## Viewing your component

To test your new Django view, run the following command to start up a development web server.

```bash linenums="0"
python manage.py runserver
```

Now you can navigate to your **Django project** URL that contains a ReactPy component, such as [`http://127.0.0.1:8000/example/`](http://127.0.0.1:8000/example/) ([_from the previous step_](#setting-up-a-django-view)).

If you copy-pasted our example component, you will now see your component display "Hello World".

??? warning "Do not use `manage.py runserver` for production"

    This command is only intended for development purposes. For production deployments make sure to read [Django's documentation](https://docs.djangoproject.com/en/dev/howto/deployment/).

## Learn more

**Congratulations!** If you followed the previous steps, you have now created a "Hello World" component using ReactPy-Django!

!!! info "Deep Dive"

    The docs you are reading only covers our Django integration. To learn more, check out one of the following links:

    -   [ReactPy-Django Feature Reference](../reference/components.md)
    -   [ReactPy Core Documentation](https://reactpy.dev/docs/guides/creating-interfaces/index.html)
    -   [Ask Questions on Discord](https://discord.gg/uNb5P4hA9X)

    Additionally, the vast majority of tutorials/guides you find for ReactJS can be applied to ReactPy.
