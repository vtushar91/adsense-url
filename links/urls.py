from django.urls import path
from .views import CreateShortLinkView, MyLinksView, DestinationView

urlpatterns = [
    path("create-short-links/", CreateShortLinkView.as_view()),
    path("my-links/", MyLinksView.as_view()),
    path("<str:short_code>/destination/", DestinationView.as_view()),
]