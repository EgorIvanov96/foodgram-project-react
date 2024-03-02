# from django import forms
from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Follow, User


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
admin.site.register(Follow)
admin.site.unregister(Group)
admin.site.empty_value_display = 'Не задано'
