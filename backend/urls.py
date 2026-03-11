from django.contrib import admin
from django.urls import path, include
from links.views import RedirectView
from .health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),  
    path('api/auth/', include('users.urls')),
    path("api/links/", include("links.urls")),
    path("<str:short_code>/", RedirectView.as_view()),
]
