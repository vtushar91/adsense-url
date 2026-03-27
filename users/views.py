from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from links.models import ShortLink
from decimal import Decimal

from .serializers import RegisterSerializer, LoginSerializer,UserProfileSerializer


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

        links = ShortLink.objects.filter(owner=user)

        links_created = links.count()
        total_clicks = sum(link.unique_clicks for link in links)

        earnings = user.earnings
        pending = user.pending_withdraw
        available = earnings - pending

        referrals = user.referrals.all()

        return Response({
            "username": user.username,

            "links_created": links_created,
            "total_clicks": total_clicks,
            "earnings": earnings,

            "available_balance": available,
            "pending_withdraw": pending,
            "total_withdrawn": user.total_withdrawn,

            "referral_code": user.referral_code,
            "total_referrals": referrals.count(),

            "referrals": [
                {
                    "username": ref.username,
                    "date_joined": ref.date_joined
                }
                for ref in referrals
            ]
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