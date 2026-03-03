from django.urls import re_path
from realtime import consumers
from realtime.consumers import DirectMessageConsumer, NotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/course/(?P<course_id>\d+)/$", consumers.CourseChatConsumer.as_asgi()),
    re_path(r"ws/dm/(?P<other_user_id>\d+)/$", DirectMessageConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
]