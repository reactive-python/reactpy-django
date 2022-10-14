<!--todo-model-start-->

```python linenums="1"
from django.db import models

class TodoItem(models.Model):
    text = models.CharField(max_length=255)
```

<!--todo-model-end-->
