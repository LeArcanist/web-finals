from django.urls import path
from .api import CourseListAPIView, CourseDetailAPIView

urlpatterns = [
    path("courses/", CourseListAPIView.as_view(), name="api_course_list"),
    path("courses/<int:pk>/", CourseDetailAPIView.as_view(), name="api_course_detail"),
]