from django.contrib import admin
from .models import ClickEvent


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):

    list_display = (
        "short_link",
        "ip_address",
        "is_unique",
        "is_completed"
        "created_at",
    )

    search_fields = (
        "short_link__short_code",
        "ip_address",
    )

    list_filter = (
        "is_unique",
        "created_at",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "short_link",
        "ip_address",
        "user_agent",
        "is_unique",
        "created_at",
    )