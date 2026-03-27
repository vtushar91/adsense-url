from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from rest_framework.permissions import AllowAny
from datetime import timedelta
from django.conf import settings
from .models import ShortLink
from .serializers import CreateShortLinkSerializer, ShortLinkSerializer
from clicks.models import ClickEvent


class CreateShortLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateShortLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        link = ShortLink.objects.create(
            owner=request.user,
            original_url=serializer.validated_data["original_url"]
        )

        short_url = f"{request.scheme}://{request.get_host()}/{link.short_code}"

        return Response({
            "short_url": short_url,
            "short_code":link.short_code
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

    def get(self, request, short_code):

        link = get_object_or_404(ShortLink, short_code=short_code)

        ip = request.META.get("REMOTE_ADDR")
        ua = request.META.get("HTTP_USER_AGENT", "")

        exists = ClickEvent.objects.filter(
            short_link=link,
            ip_address=ip,
            user_agent=ua,
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).exists()

        is_unique = not exists

        ClickEvent.objects.create(
            short_link=link,
            ip_address=ip,
            user_agent=ua,
            is_unique=is_unique
        )

        if is_unique:
            link.unique_clicks += 1
            link.save(update_fields=["unique_clicks"])

        host = request.get_host()

        if "localhost" in host or "127.0.0.1" in host:
            base_url = settings.LOCAL_ADS_FRONTEND_URL
        else:
            base_url = settings.PROD_ADS_FRONTEND_URL

        ads_redirect_url = f"{base_url}?code={short_code}"

        return redirect(ads_redirect_url)
    
class DestinationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, short_code):

        link = get_object_or_404(ShortLink, short_code=short_code)

        return Response({
            "destination": link.original_url
        })