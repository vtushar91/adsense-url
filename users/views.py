from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from links.models import ShortLink
from decimal import Decimal
from clicks.models import ClickEvent
from .serializers import RegisterSerializer, LoginSerializer,UserProfileSerializer
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),  
            "user": {
                "username": user.username,
                "name": user.name
            }
        }, status=status.HTTP_200_OK)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.profile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Base queryset (reuse everywhere)
        base_qs = ClickEvent.objects.filter(short_link__owner=user)

        # 🔢 Overall stats (SINGLE QUERY)
        stats = base_qs.aggregate(
            total_clicks=Count("id"),
            unique_clicks=Count("id", filter=Q(is_unique=True)),
            completed_clicks=Count("id", filter=Q(is_completed=True)),
            total_earnings=Sum("earned_amount", filter=Q(is_completed=True)),
            avg_cpm=Avg("cpm_snapshot", filter=Q(is_completed=True)),
        )

        # 📅 Today stats (SINGLE QUERY)
        today_qs = base_qs.filter(created_at__date=today)

        today_stats = today_qs.aggregate(
            total_clicks=Count("id"),
            unique_clicks=Count("id", filter=Q(is_unique=True)),
            completed_clicks=Count("id", filter=Q(is_completed=True)),
            earnings=Sum("earned_amount", filter=Q(is_completed=True)),
        )

        # 🔗 Links count
        links_created = ShortLink.objects.filter(owner=user).count()

        # 👥 Referrals
        referral_count = user.referrals.count()
        referral_earnings = getattr(user, "referral_earnings", 0)

        # 💰 Wallet
        total_earnings = stats["total_earnings"] or Decimal("0")
        pending = user.pending_withdraw or Decimal("0")
        available = total_earnings - pending

        # 📈 Last 7 days performance
        last_7_days = []

        for i in range(6, -1, -1):
            day = today - timedelta(days=i)

            day_qs = base_qs.filter(created_at__date=day)

            day_data = day_qs.aggregate(
                clicks=Count("id"),
                unique_clicks=Count("id", filter=Q(is_unique=True)),
                completed_clicks=Count("id", filter=Q(is_completed=True)),
                earnings=Sum("earned_amount", filter=Q(is_completed=True)),
            )

            last_7_days.append({
                "date": str(day),
                "clicks": day_data["clicks"] or 0,
                "unique_clicks": day_data["unique_clicks"] or 0,
                "completed_clicks": day_data["completed_clicks"] or 0,
                "earnings": float(day_data["earnings"] or 0),
            })

        return Response({
            "username": user.username,

            # 🔥 Top cards (today)
            "today": {
                "views": today_stats["total_clicks"] or 0,
                "unique_views": today_stats["unique_clicks"] or 0,
                "completed_views": today_stats["completed_clicks"] or 0,
                "earnings": float(today_stats["earnings"] or 0),
            },

            # 📊 Overall stats
            "overall": {
                "links_created": links_created,
                "total_views": stats["total_clicks"] or 0,
                "total_unique_views": stats["unique_clicks"] or 0,
                "total_completed_views": stats["completed_clicks"] or 0,
                "total_earnings": float(total_earnings),
                "average_cpm": float(stats["avg_cpm"] or 0),
            },

            # 💰 Wallet
            "wallet": {
                "available_balance": float(available),
                "pending_withdraw": float(pending),
                "total_withdrawn": float(user.total_withdrawn or 0),
            },

            # 👥 Referrals
            "referrals": {
                "code": user.referral_code,
                "count": referral_count,
                "earnings": float(referral_earnings),
            },

            # 📈 Graph
            "performance": last_7_days,
        })
class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        amount = Decimal(request.data.get("amount", "0"))

        available = float(user.earnings - user.pending_withdraw)

        if amount <= 0:
            return Response({"error": "Invalid amount"}, status=400)

        if amount > available:
            return Response({"error": "Insufficient balance"}, status=400)

        user.pending_withdraw += amount
        user.save(update_fields=["pending_withdraw"])

        return Response({
            "message": "Withdraw request submitted",
            "pending_withdraw": user.pending_withdraw
        })