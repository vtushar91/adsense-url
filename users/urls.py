from django.urls import path
from .views import RegisterView, LoginView, ProfileView, DashboardView, WithdrawView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('user-profile/', ProfileView.as_view()),
    path("dashboard/", DashboardView.as_view()),
    path("withdraw/", WithdrawView.as_view()),
]
