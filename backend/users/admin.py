from django.contrib import admin

from .models import User


class CastomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    list_editable = (
        'email',
        'first_name',
        'last_name'
    )
    search_fields = (
        'email',
        'username'
    )
    list_filter = (
        'email',
        'username'
    )


admin.site.register(User, CastomUserAdmin)
admin.site.empty_value_display = 'Не задано'
