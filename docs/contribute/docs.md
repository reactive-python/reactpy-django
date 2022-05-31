If you plan to make changes to this documentation, you'll need to install the following dependencies first:

-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

Once done, you should clone this repository:

```bash
git clone https://github.com/idom-team/django-idom.git
cd django-idom
```

Then, by running the command below you can:

-   Install an editable version of the documentation
-   Self-host a test server for the documentation

```bash
pip install -r ./requirements/build-docs.txt --upgrade
```

Finally, to verify that everything is working properly, you can manually run the docs preview webserver.

```bash
mkdocs serve
```

Navigate to `http://127.0.0.1:8000` to view a preview of the documentation.
