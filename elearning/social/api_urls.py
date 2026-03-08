from django.urls import path
from .api import StatusUpdateListAPIView

urlpatterns = [
    path("status-updates/", StatusUpdateListAPIView.as_view(), name="api_status_updates"),
]