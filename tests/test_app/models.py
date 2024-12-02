from django.db import models


class TodoItem(models.Model):
    done = models.BooleanField()
    text = models.CharField(max_length=1000, unique=True)


class AsyncTodoItem(models.Model):
    done = models.BooleanField()
    text = models.CharField(max_length=1000, unique=True)


class RelationalChild(models.Model):
    text = models.CharField(max_length=1000)


class AsyncRelationalChild(models.Model):
    text = models.CharField(max_length=1000)


class RelationalParent(models.Model):
    done = models.BooleanField(default=True)
    many_to_many = models.ManyToManyField(RelationalChild, related_name="many_to_many")
    one_to_one = models.OneToOneField(RelationalChild, related_name="one_to_one", on_delete=models.SET_NULL, null=True)


class AsyncRelationalParent(models.Model):
    done = models.BooleanField(default=True)
    many_to_many = models.ManyToManyField(AsyncRelationalChild, related_name="many_to_many")
    one_to_one = models.OneToOneField(
        AsyncRelationalChild,
        related_name="one_to_one",
        on_delete=models.SET_NULL,
        null=True,
    )


class ForiegnChild(models.Model):
    text = models.CharField(max_length=1000)
    parent = models.ForeignKey(RelationalParent, related_name="many_to_one", on_delete=models.CASCADE)


class AsyncForiegnChild(models.Model):
    text = models.CharField(max_length=1000)
    parent = models.ForeignKey(AsyncRelationalParent, related_name="many_to_one", on_delete=models.CASCADE)
