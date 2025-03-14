# ruff: noqa: RUF012
from django.contrib import admin

from reactpy_django.models import ComponentSession, Config, UserDataModel
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
    list_display = ["uuid", "last_accessed"]


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ["pk", "cleaned_at"]


@admin.register(UserDataModel)
class UserDataModelAdmin(admin.ModelAdmin):
    list_display = ["user_pk", "data"]
