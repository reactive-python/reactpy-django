## Overview

<p class="intro" markdown>

Run a webserver to display your Django view.

</p>

---

## Viewing your component using a webserver

To test your new Django view, run the following command to start up a development webserver.

```bash linenums="0"
python manage.py runserver
```

Now you can navigate to your **Django project** URL that contains a ReactPy component, such as [`http://127.0.0.1:8000/example/`](http://127.0.0.1:8000/example/) ([_from the previous step_](./register-view.md)).

If you copy-pasted our example component, you will now see your component display "Hello World".

!!! warning "Pitfall"

    Do not use `manage.py runserver` for production.

    This command is only intended for development purposes. For production deployments make sure to read [Django's documentation](https://docs.djangoproject.com/en/dev/howto/deployment/).
