## Overview

<p class="intro" markdown>

    You will need to set up a Python environment to develop ReactPy-Django.

</p>

!!! note

    Looking to contribute features that are not Django specific?

    Everything within the `reactpy-django` repository must be specific to Django integration. Check out the [ReactPy Core documentation](https://reactpy.dev/docs/about/contributor-guide.html) to contribute general features such as components, hooks, and events.

---

## Creating an environment

If you plan to make code changes to this repository, you will need to install the following dependencies first:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)
-   [NPM](https://docs.npmjs.com/try-the-latest-stable-version-of-npm) for installing and managing Javascript

Once done, you should clone this repository:

```bash linenums="0"
git clone https://github.com/reactive-python/reactpy-django.git
cd reactpy-django
```

Then, by running the command below you can:

-   Install an editable version of the Python code
-   Download, build, and install Javascript dependencies

```bash linenums="0"
pip install -e . -r requirements.txt --verbose --upgrade
```

!!! warning "Pitfall"

    Some of our development dependencies require a C++ compiler, which is not installed by default on Windows.

    If you receive errors related to this during installation, follow the instructions in your console errors.

Finally, to verify that everything is working properly, you can manually run the test web server.

```bash linenums="0"
cd tests
python manage.py runserver
```

Navigate to [`http://127.0.0.1:8000`](http://127.0.0.1:8000) to see if the tests are rendering correctly.

## Creating a pull request

{% include-markdown "../../includes/pr.md" %}

## Running the full test suite

!!! note

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
