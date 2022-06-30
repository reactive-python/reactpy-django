## Get Component

You can fetch any of your IDOM components from other files by using `get_component`.

```python title="components.py"
from idom import component
from django_idom.utils import get_component

@component
def MyComponent():
    hello_world = get_component("example_project.my_app.components.HelloWorld")
    return hello_world(recipient="World")
```

??? question "Should I use this instead of `#!python import`?"

    TBD