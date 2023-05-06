## Overview

!!! summary

    Run a webserver to display your Django view.

---

## Run the Webserver

To test your new Django view, run the following command to start up a development webserver.

```bash linenums="0"
python manage.py runserver
```

Now you can navigate to your **Django project** URL that contains an ReactPy component, such as `http://127.0.0.1:8000/example/` (_from the previous step_).

If you copy-pasted our example component, you will now see your component display "Hello World".

??? warning "Do not use `manage.py runserver` for production."

    The webserver contained within `manage.py runserver` is only intended for development and testing purposes. For production deployments make sure to read [Django's documentation](https://docs.djangoproject.com/en/dev/howto/deployment/).
