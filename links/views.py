from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from rest_framework.permissions import AllowAny
from datetime import timedelta
from django.conf import settings
from django.db import models
from .models import ShortLink, Announcement, MonetizationRule
from .serializers import CreateShortLinkSerializer, ShortLinkSerializer
from clicks.models import ClickEvent
from decimal import Decimal
class CreateShortLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateShortLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        rule_id = serializer.validated_data.get("monetization_rule_id")

        # 🎯 Get monetization rule
        if rule_id:
            try:
                rule = MonetizationRule.objects.get(
                    id=rule_id,
                    is_active=True
                )

            except MonetizationRule.DoesNotExist:
                return Response({"error": "Invalid rule"}, status=400)

        else:
            # fallback to default rule
            rule = MonetizationRule.objects.filter(
                is_active=True,
                is_default=True
            ).first()

            if not rule:
                return Response({
                    "error": "No default monetization rule configured"
                }, status=500)

        # ✅ Create link
        link = ShortLink.objects.create(
            owner=user,
            original_url=serializer.validated_data["original_url"],
            monetization=rule
        )
        short_url = f"{settings.BASE_DOMAIN}/{link.short_code}/"
        return Response({
            "short_url": short_url,
            "short_code": link.short_code
        })


class MyLinksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        links = ShortLink.objects.filter(owner=request.user).order_by("-created_at")
        serializer = ShortLinkSerializer(
            links,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)

class RedirectView(APIView):
    permission_classes = []
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def get(self, request, short_code):
        link = get_object_or_404(ShortLink, short_code=short_code)

        ip = self.get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        now = timezone.now()

        # 🔍 Check uniqueness (last 24h)
        exists = ClickEvent.objects.filter(
            short_link=link,
            ip_address=ip,
            user_agent=ua,
            created_at__gte=now - timedelta(hours=24)
        ).exists()

        is_unique = not exists

        # Create click event
        ClickEvent.objects.create(
            short_link=link,
            ip_address=ip,
            user_agent=ua,
            is_unique=is_unique
        )

        # Increment unique clicks safely
        if is_unique:
            ShortLink.objects.filter(id=link.id).update(
                unique_clicks=models.F("unique_clicks") + 1
            )

        # Redirect to ads frontend
        host = request.get_host()

        if "localhost" in host or "127.0.0.1" in host:
            base_url = settings.LOCAL_ADS_FRONTEND_URL
        else:
            base_url = settings.PROD_ADS_FRONTEND_URL

        ads_redirect_url = f"{base_url}/code={short_code}"

        return redirect(ads_redirect_url)
class DestinationView(APIView):
    permission_classes = [AllowAny]
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
    def get(self, request, short_code):
        link = get_object_or_404(ShortLink, short_code=short_code)

        ip = self.get_client_ip(request)
        ua = request.META.get("HTTP_USER_AGENT", "")

        # Get latest incomplete event
        event = (
            ClickEvent.objects
            .filter(
                short_link=link,
                ip_address=ip,
                user_agent=ua,
                is_completed=False
            )
            .order_by("-created_at")
            .first()
        )

        # Mark completion + calculate earning
        if event and not event.is_completed:
            event.is_completed = True

            if link.monetization:
                cpm = link.monetization.cpm
                earning = Decimal(cpm) / Decimal(1000)
                event.earned_amount = earning
                event.cpm_snapshot = cpm
                # 💰 ADD USER EARNING
                user = link.owner
                user.earnings += earning
                user.save(update_fields=["earnings"])

                # 💸 REFERRAL EARNING (NEW 🔥)
                if user.referred_by:
                    referrer = user.referred_by

                    bonus = earning * settings.REFERRAL_PERCENT

                    referrer.earnings += bonus
                    referrer.referral_earnings += bonus

                    referrer.save(update_fields=["earnings", "referral_earnings"])
            event.save(update_fields=[
                "is_completed",
                "earned_amount",
                "cpm_snapshot"
            ])

        return Response({
            "destination": link.original_url
        })
class AnnouncementListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        announcements = (
            Announcement.objects
            .filter(is_active=True)
            .filter(
                models.Q(start_at__isnull=True) | models.Q(start_at__lte=now)
            )
            .filter(
                models.Q(end_at__isnull=True) | models.Q(end_at__gte=now)
            )
            .order_by("-created_at")
        )

        data = [
            {
                "id": str(a.id),
                "title": a.title,
                "message": a.message,
                "created_at":a.created_at,
            }
            for a in announcements
        ]

        return Response({"announcements": data})
class MonetizationRuleListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_level = getattr(user, "level", 0)

        rules = (
            MonetizationRule.objects
            .filter(is_active=True, min_user_level__lte=user_level)
            .order_by("ad_pages")
        )

        data = [
            {
                "id": str(rule.id),
                "name": rule.name,
                "ad_pages": rule.ad_pages,
                "cpm": str(rule.cpm),
            }
            for rule in rules
        ]
        return Response({
            "rules": data
        })