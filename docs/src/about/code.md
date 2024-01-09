## Overview

<p class="intro" markdown>

    You will need to set up a Python environment to develop ReactPy-Django.

</p>

!!! abstract "Note"

    Looking to contribute features that are not Django specific?

    Everything within the `reactpy-django` repository must be specific to Django integration. Check out the [ReactPy Core documentation](https://reactpy.dev/docs/about/contributor-guide.html) to contribute general features such as components, hooks, and events.

---

## Creating an environment

If you plan to make code changes to this repository, you will need to install the following dependencies first:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

Once done, you should clone this repository:

```bash linenums="0"
git clone https://github.com/reactive-python/reactpy-django.git
cd reactpy-django
```

Then, by running the command below you can install the dependencies needed to run the ReactPy Django development environment.

```bash linenums="0"
pip install -r requirements.txt --upgrade --verbose
```

!!! warning "Pitfall"

    Some of our development dependencies require a C++ compiler, which is not installed by default on Windows. If you receive errors related to this during installation, follow the instructions in your console errors.

    Additionally, be aware that ReactPy Django's JavaScript bundle is built within the following scenarios:

    1. When `pip install` is run on the `reactpy-django` package.
    2. Every time `python manage.py ...` or `nox ...` is run

## Running the full test suite

!!! abstract "Note"

    This repository uses [Nox](https://nox.thea.codes/en/stable/) to run tests. For a full test of available scripts run `nox -l`.

By running the command below you can run the full test suite:

```bash linenums="0"
nox -s test
```

Or, if you want to run the tests in the background:

```bash linenums="0"
nox -s test -- --headless
```

## Running Django tests

If you want to only run our Django tests in your current environment, you can use the following command:

```bash linenums="0"
cd tests
python manage.py test
```

## Running Django test web server

If you want to manually run the Django test application, you can use the following command:

```bash linenums="0"
cd tests
python manage.py runserver
```

## Creating a pull request

{% include-markdown "../../includes/pr.md" %}
