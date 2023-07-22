## Overview

!!! summary "Overview"

    You will need to set up a Python environment to develop ReactPy-Django.

??? tip "Looking to contribute features that are not Django specific?"

    Everything within the `reactpy-django` repository must be specific to Django integration. Check out the [ReactPy Core documentation](https://reactpy.dev/docs/about/contributor-guide.html) to contribute general features such as: components, hooks, events, and more.

## Modifying Code

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
pip install -e . -r requirements.txt
```

Finally, to verify that everything is working properly, you can manually run the test webserver.

```bash linenums="0"
cd tests
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000` to see if the tests are rendering correctly.

## GitHub Pull Request

{% include-markdown "../../includes/pr.md" %}
