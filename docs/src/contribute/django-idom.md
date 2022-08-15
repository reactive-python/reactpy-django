???+ tip "Looking to contribute features that are not Django specific?"

    Everything within the `django-idom` repository must be specific to Django integration. Check out the [IDOM Core documentation](https://idom-docs.herokuapp.com/docs/about/contributor-guide.html) to contribute general features such as: components, hooks, events, and more.

If you plan to make code changes to this repository, you'll need to install the following dependencies first:

-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)
-   [NPM](https://docs.npmjs.com/try-the-latest-stable-version-of-npm) for installing and managing Javascript
-   [ChromeDriver](https://chromedriver.chromium.org/downloads) for testing with [Selenium](https://www.seleniumhq.org/)

Once done, you should clone this repository:

```bash
git clone https://github.com/idom-team/django-idom.git
cd django-idom
```

Then, by running the command below you can:

-   Install an editable version of the Python code
-   Download, build, and install Javascript dependencies

```bash
pip install -e . -r requirements.txt
```

Finally, to verify that everything is working properly, you can manually run the development webserver.

```bash
cd tests
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000` to see if the tests are rendering correctly.
