from django.contrib import admin
from test_app.models import (
    AsyncForiegnChild,
    AsyncRelationalChild,
    AsyncRelationalParent,
    AsyncTodoItem,
    ForiegnChild,
    RelationalChild,
    RelationalParent,
    TodoItem,
)

from reactpy_django.models import ComponentSession


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    pass


@admin.register(RelationalChild)
class RelationalChildAdmin(admin.ModelAdmin):
    pass


@admin.register(RelationalParent)
class RelationalParentAdmin(admin.ModelAdmin):
    pass


@admin.register(ForiegnChild)
class ForiegnChildAdmin(admin.ModelAdmin):
    pass


@admin.register(AsyncTodoItem)
class AsyncTodoItemAdmin(admin.ModelAdmin):
    pass


@admin.register(AsyncRelationalChild)
class AsyncRelationalChildAdmin(admin.ModelAdmin):
    pass


@admin.register(AsyncRelationalParent)
class AsyncRelationalParentAdmin(admin.ModelAdmin):
    pass


@admin.register(AsyncForiegnChild)
class AsyncForiegnChildAdmin(admin.ModelAdmin):
    pass


@admin.register(ComponentSession)
class ComponentSessionAdmin(admin.ModelAdmin):
    list_display = ("uuid", "last_accessed")
