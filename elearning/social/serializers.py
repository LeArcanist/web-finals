from rest_framework import serializers
from .models import StatusUpdate


class StatusUpdateSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = StatusUpdate
        fields = ["id", "author", "author_username", "content", "created_at"]