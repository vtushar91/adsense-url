from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # What you see in user list
    list_display = ('username', 'name', 'phone_or_upi', 'is_active')
    search_fields = ('username', 'phone_or_upi')
    ordering = ('-date_joined',)

    # Fields shown when ADDING a user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'phone_or_upi', 'password1', 'password2'),
        }),
    )

    # Fields shown when EDITING a user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Basic Info', {'fields': ('name', 'phone_or_upi')}),
        ('Status', {'fields': ('is_active',)}),
    )

    # Hide advanced Django stuff
    filter_horizontal = ()
    list_filter = ()
    