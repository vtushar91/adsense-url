from rest_framework import serializers
from .models import ShortLink
from django.conf import settings

class CreateShortLinkSerializer(serializers.ModelSerializer):
    monetization_rule_id = serializers.UUIDField(required=False)

    class Meta:
        model = ShortLink
        fields = ["original_url", "monetization_rule_id"]


class ShortLinkSerializer(serializers.ModelSerializer):
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortLink
        fields = [
            "short_url",
            "original_url",
            "unique_clicks",
            "created_at"
        ]

    def get_short_url(self, obj):
        request = self.context.get("request")
        return f"{settings.BASE_DOMAIN}/{obj.short_code}/"