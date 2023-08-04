from django.db import models


class TodoItem(models.Model):
    done = models.BooleanField()  # type: ignore
    text = models.CharField(max_length=1000, unique=True)  # type: ignore


class AsyncTodoItem(models.Model):
    done = models.BooleanField()  # type: ignore
    text = models.CharField(max_length=1000, unique=True)  # type: ignore


class RelationalChild(models.Model):
    text = models.CharField(max_length=1000)  # type: ignore


class AsyncRelationalChild(models.Model):
    text = models.CharField(max_length=1000)  # type: ignore


class RelationalParent(models.Model):
    done = models.BooleanField(default=True)  # type: ignore
    many_to_many = models.ManyToManyField(RelationalChild, related_name="many_to_many")  # type: ignore
    one_to_one = models.OneToOneField(  # type: ignore
        RelationalChild, related_name="one_to_one", on_delete=models.SET_NULL, null=True
    )


class AsyncRelationalParent(models.Model):
    done = models.BooleanField(default=True)  # type: ignore
    many_to_many = models.ManyToManyField(AsyncRelationalChild, related_name="many_to_many")  # type: ignore
    one_to_one = models.OneToOneField(  # type: ignore
        AsyncRelationalChild,
        related_name="one_to_one",
        on_delete=models.SET_NULL,
        null=True,
    )


class ForiegnChild(models.Model):
    text = models.CharField(max_length=1000)  # type: ignore
    parent = models.ForeignKey(RelationalParent, related_name="many_to_one", on_delete=models.CASCADE)  # type: ignore


class AsyncForiegnChild(models.Model):
    text = models.CharField(max_length=1000)  # type: ignore
    parent = models.ForeignKey(AsyncRelationalParent, related_name="many_to_one", on_delete=models.CASCADE)  # type: ignore
