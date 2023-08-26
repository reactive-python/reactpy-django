## Overview

<p class="intro" markdown>

You will need to set up a Python environment to run the ReactPy-Django test suite.

</p>

---

## Running Tests

This repository uses [Nox](https://nox.thea.codes/en/stable/) to run tests. For a full test of available scripts run `nox -l`.

If you plan to run tests, you will need to install the following dependencies first:

-   [Python 3.9+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

Once done, you should clone this repository:

```bash linenums="0"
git clone https://github.com/reactive-python/reactpy-django.git
cd reactpy-django
pip install -e . -r requirements.txt --upgrade
```

## Full Test Suite

By running the command below you can run the full test suite:

```bash linenums="0"
nox -s test
```

Or, if you want to run the tests in the background:

```bash linenums="0"
nox -s test -- --headless
```

## Django Tests

If you want to only run our Django tests in your current environment, you can use the following command:

```bash linenums="0"
cd tests
python manage.py test
```

## Django Test Webserver

If you want to manually run the Django test application, you can use the following command:

```bash linenums="0"
cd tests
python manage.py runserver
```
