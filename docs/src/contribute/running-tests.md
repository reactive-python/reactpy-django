This repository uses [Nox](https://nox.thea.codes/en/stable/) to run tests. For a full test of available scripts run `nox -l`.

If you plan to run tests, you will need to install the following dependencies first:

-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads)

Once done, you should clone this repository:

```bash
git clone https://github.com/idom-team/django-idom.git
cd django-idom
pip install -r ./requirements/test-run.txt --upgrade
```

Then, by running the command below you can run the full test suite:

```
nox -s test
```

Or, if you want to run the tests in the foreground:

```
nox -s test -- --headed
```
