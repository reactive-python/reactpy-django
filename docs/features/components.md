## Static CSS

Allows you to defer loading a CSS stylesheet until a component begins rendering. This stylesheet must be stored within [Django's static files](https://docs.djangoproject.com/en/dev/howto/static-files/).

```python title="components.py"
from idom import component, html
from django_idom.components import static_css

@component
def MyComponent():
    return html.div(
        static_css("/static/css/buttons.css"),
        html.button("My Button!")
    )
```

??? question "Should I put `static_css` at the top of my component?"

<!-- Yes, to ensure proper load order -->

??? question "Can I load HTML using `html.link`?"

??? question "What about external stylesheets?"

??? question "Why not load my CSS in `#!html <head>`?"

<!-- Generally, Django stylesheets are loaded in your `#!html <head>` using the `#!jinja {% load static %}` template tag.  -->

## Static JavaScript

<!-- In progress -->
