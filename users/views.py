from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from links.models import ShortLink
from decimal import Decimal
from clicks.models import ClickEvent
from .serializers import RegisterSerializer, LoginSerializer,UserProfileSerializer
from django.db.models import Sum, Avg
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

        links = ShortLink.objects.filter(owner=user)

        # 🔢 Basic stats
        links_created = links.count()

        total_clicks = links.aggregate(
            total=Sum("unique_clicks")
        )["total"] or 0

        # 📅 Today clicks
        today_clicks = ClickEvent.objects.filter(
            short_link__owner=user,
            created_at__date=today
        ).count()

        # 💰 Earnings (total)
        earnings_data = ClickEvent.objects.filter(
            short_link__owner=user,
            is_completed=True
        ).aggregate(
            total=Sum("earned_amount")
        )

        total_earnings = earnings_data["total"] or 0

        # 💰 Today earnings
        today_earnings_data = ClickEvent.objects.filter(
            short_link__owner=user,
            is_completed=True,
            created_at__date=today
        ).aggregate(
            total=Sum("earned_amount")
        )

        today_earnings = today_earnings_data["total"] or 0

        # 📊 Average CPM
        avg_cpm = ClickEvent.objects.filter(
            short_link__owner=user,
            is_completed=True
        ).aggregate(
            avg=Avg("cpm_snapshot")
        )["avg"] or 0

        # 👥 Referrals
        referrals = user.referrals.all()
        referral_count = referrals.count()

        # 💰 (optional: if you track referral earnings)
        referral_earnings = getattr(user, "referral_earnings", 0)

        # 💸 Balance
        pending = user.pending_withdraw or 0
        available = total_earnings - pending

        # 📈 Performance graph (last 7 days)
        last_7_days = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)

            day_queryset = ClickEvent.objects.filter(
                short_link__owner=user,
                created_at__date=day
            )

            # 💰 earnings
            day_earnings = day_queryset.filter(
                is_completed=True
            ).aggregate(total=Sum("earned_amount"))["total"] or 0

            # 👆 clicks (ALL clicks, not just completed)
            day_clicks = day_queryset.count()

            last_7_days.append({
                "date": str(day),
                "earnings": float(day_earnings),
                "clicks": day_clicks
            })

        return Response({
            "username": user.username,

            # 🔥 top cards
            "today_views": today_clicks,
            "today_earnings": today_earnings,
            "referral_earnings": referral_earnings,
            "average_cpm": avg_cpm,

            # 📊 stats
            "links_created": links_created,
            "total_views": total_clicks,
            "total_earnings": total_earnings,

            # 💰 wallet
            "available_balance": available,
            "pending_withdraw": pending,
            "total_withdrawn": user.total_withdrawn or 0,

            # 👥 referrals
            "referral_code": user.referral_code,
            "total_referrals": referral_count,

            # 📈 graph
            "performance": last_7_days
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