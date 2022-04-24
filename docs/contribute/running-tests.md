This repo uses [Nox](https://nox.thea.codes/en/stable/) to run scripts which can be found in `noxfile.py`. For a full test of available scripts run `nox -l`. To run the full test suite simple execute:

```
nox -s test
```

To run the tests using a headless browser:

```
nox -s test -- --headless
```
