Integrated within Django IDOM, we bundle a template tag. Within this tag, you can pass in keyworded parameters directly into your component.

```jinja
{% load idom %}
<!DOCTYPE html>
<html>
  <body>
    {% component "example.components.HelloComponent" recipient="World" %}
  </body>
</html>
```

!!! note "Note: Multiple Components on One Page"

    You can add as many components to a webpage as needed by using the template tag multiple times. Retrofitting legacy sites to use reactive components will typically involve many components on one page.

    But keep in mind, in scenarios where you are trying to create a Single Page Application (SPA) within Django, you will only have one central component within your body tag as shown below.

---

For this template tag, there are only two reserved parameters: `class` and `key`

-   `class` allows you to apply a HTML class to the top-level component div. This is useful for styling purposes.
-   `key` allows you to force the component to use a [specific key value](https://idom-docs.herokuapp.com/docs/guides/understanding-idom/why-idom-needs-keys.html?highlight=key). You typically won't need to set this.

```jinja
{% component "example.components.MyComponent" class="my-html-class" key=123 %}
```
