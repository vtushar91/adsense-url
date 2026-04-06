from django.contrib import admin
from .models import ShortLink, MonetizationRule, Announcement


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
@admin.register(MonetizationRule)
class MonetizationRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "ad_pages", "cpm", "min_user_level", "is_active")
    list_filter = ("is_active", "min_user_level")
    search_fields = ("name",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "start_at", "end_at", "min_user_level")
    list_filter = ("is_active",)
    search_fields = ("title",)