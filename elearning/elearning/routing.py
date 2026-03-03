from django.urls import re_path
from realtime import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/course/(?P<course_id>\d+)/$", consumers.CourseChatConsumer.as_asgi()),
]