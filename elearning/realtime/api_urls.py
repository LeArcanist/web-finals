from django.urls import path
from .api import NotificationListAPIView

urlpatterns = [
    path("notifications/", NotificationListAPIView.as_view(), name="api_notifications"),
]