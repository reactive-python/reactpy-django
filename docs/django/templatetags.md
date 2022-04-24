Integrated within Django IDOM, we bundle a template tag. Within this tag, you can pass in keyworded parameters.

!!! note

    You can add as many components to a webpage as needed. Retrofitting legacy sites to use reactive components will typically involve many components.

    But keep in mind, in scenarios where you are trying to create a Single Page Application (SPA) within Django, you will only have one central component within your body tag as shown below.

```jinja
{% load idom %}
<!DOCTYPE html>
<html>
  <body>
    {% component "example.components.HelloComponent" recipient="World" %}
  </body>
</html>
```

There are only two reserved parameters: `class` and `key`

-   `class` allows you to apply a HTML class to the top-level component div. This is useful for styling purposes.
-   `key` allows you to force the component to use a [specific key value](https://idom-docs.herokuapp.com/docs/guides/understanding-idom/why-idom-needs-keys.html?highlight=key) within the front-end client. You typically won't need to change this.

```jinja
{% component "example.components.HelloComponent" class="my-html-class" key=123 %}
```
