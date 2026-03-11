from django.contrib import admin
from .models import ShortLink


@admin.register(ShortLink)
class ShortLinkAdmin(admin.ModelAdmin):

    list_display = (
        "short_code",
        "owner",
        "original_url",
        "unique_clicks",
        "created_at",
    )

    search_fields = (
        "short_code",
        "original_url",
        "owner__username",
    )

    list_filter = (
        "created_at",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "short_code",
        "unique_clicks",
        "created_at",
    )