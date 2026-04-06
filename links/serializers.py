from rest_framework import serializers
from .models import ShortLink


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
        return f"{request.scheme}://{request.get_host()}/{obj.short_code}"