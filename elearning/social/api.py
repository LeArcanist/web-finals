from rest_framework import generics, permissions
from .models import StatusUpdate
from .serializers import StatusUpdateSerializer


class StatusUpdateListAPIView(generics.ListAPIView):
    serializer_class = StatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return StatusUpdate.objects.order_by("-created_at")