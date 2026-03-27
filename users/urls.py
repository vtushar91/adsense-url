from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileView, DashboardView, WithdrawView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('user-profile/', ProfileView.as_view()),
    path("dashboard/", DashboardView.as_view()),
    path("withdraw/", WithdrawView.as_view()),
]
