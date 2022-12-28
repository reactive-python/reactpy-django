from django.contrib import admin
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
