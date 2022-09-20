This repo uses [Nox](https://nox.thea.codes/en/stable/) to run scripts which can be found in `noxfile.py`. For a full test of available scripts run `nox -l`. To run the full test suite simple execute:

```
nox -s test
```

If you do not want to run the tests in the background:

```
nox -s test -- --headed
```

!!! warning "Most tests will not run on Windows"

    Due to [bugs within Django Channels](https://github.com/django/channels/issues/1207), functional tests are not run on Windows. In order for Windows users to test Django-IDOM functionality, you will need to run tests via [Windows Subsystem for Linux](https://code.visualstudio.com/docs/remote/wsl).
