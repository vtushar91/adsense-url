from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    # List view (table)
    list_display = (
        'username',
        'name',
        'phone_or_upi',
        'earnings',
        'referral_code',
        'is_active'
    )

    search_fields = ('username', 'phone_or_upi', 'referral_code')

    ordering = ('-date_joined',)

    # Add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'phone_or_upi', 'password1', 'password2'),
        }),
    )

    # Edit user form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),

        ('Basic Info', {
            'fields': ('name', 'phone_or_upi')
        }),

        ('Earnings', {
            'fields': ('earnings', 'pending_withdraw', 'total_withdrawn')
        }),

        ('Referral', {
            'fields': ('referral_code', 'referred_by')
        }),

        ('Status', {
            'fields': ('is_active',)
        }),
    )

    # Make sensitive fields read-only
    readonly_fields = ('referral_code',)

    # Keep it clean
    filter_horizontal = ()
    list_filter = ()
    
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "city", "country")