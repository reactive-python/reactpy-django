<!--hello-world-view-start-->

```python
from django.http import HttpResponse

def hello_world_view(request, *args, **kwargs):
    return HttpResponse("Hello World!")
```

<!--hello-world-view-end-->

<!--hello-world-cbv-start-->

```python
from django.http import HttpResponse
from django.views import View

class HelloWorldView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello World!")
```

<!--hello-world-cbv-end-->