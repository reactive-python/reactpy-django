<!--hello-world-view-start-->

```python linenums="1"
from django.http import HttpResponse

def hello_world_view(request, *args, **kwargs):
    return HttpResponse("Hello World!")
```

<!--hello-world-view-end-->

<!--hello-world-cbv-start-->

```python linenums="1"
from django.http import HttpResponse
from django.views import View

class HelloWorldView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello World!")
```

<!--hello-world-cbv-end-->

<!--todo-model-start-->

```python linenums="1"
from django.db import models

class TodoItem(models.Model):
    text = models.CharField(max_length=255)
```

<!--todo-model-end-->
