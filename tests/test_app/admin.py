from django.contrib import admin
from django_reactpy.models import ComponentSession
from test_app.models import ForiegnChild, RelationalChild, RelationalParent, TodoItem


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


@admin.register(ComponentSession)
class ComponentParamsAdmin(admin.ModelAdmin):
    list_display = ("uuid", "last_accessed")
