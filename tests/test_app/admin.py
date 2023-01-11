from django.contrib import admin
from test_app.models import ForiegnChild, RelationalChild, RelationalParent, TodoItem

from django_idom.models import ComponentParams


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


@admin.register(ComponentParams)
class ComponentParamsAdmin(admin.ModelAdmin):
    list_display = ("uuid", "last_accessed")
