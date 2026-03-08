from django.urls import path
from .api import UserListAPIView, UserDetailAPIView

urlpatterns = [
    path("users/", UserListAPIView.as_view(), name="api_user_list"),
    path("users/<int:pk>/", UserDetailAPIView.as_view(), name="api_user_detail"),
]

