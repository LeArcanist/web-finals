from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    teacher_username = serializers.CharField(source="teacher.username", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "teacher", "teacher_username"]