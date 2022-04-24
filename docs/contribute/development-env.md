If you plan to make code changes to this repository, you'll need to install the following dependencies first:

- [NPM](https://docs.npmjs.com/try-the-latest-stable-version-of-npm) for
  installing and managing Javascript
- [ChromeDriver](https://chromedriver.chromium.org/downloads) for testing with
  [Selenium](https://www.seleniumhq.org/)

Once done, you should clone this repository:

```bash
git clone https://github.com/idom-team/django-idom.git
cd django-idom
```

Then, by running the command below you can:

- Install an editable version of the Python code

- Download, build, and install Javascript dependencies

```bash
pip install -e . -r requirements.txt
```

Finally, to verify that everything is working properly, you'll want to run the test suite in the next step.