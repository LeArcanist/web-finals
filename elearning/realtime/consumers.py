import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from courses.models import Course, Enrollment


class CourseChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.course_id = int(self.scope["url_route"]["kwargs"]["course_id"])
        self.room_group_name = f"course_{self.course_id}"

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        allowed = await self.user_can_access_course_chat(user.id, self.course_id)
        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]
        data = json.loads(text_data)
        message = (data.get("message") or "").strip()
        if not message:
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "username": user.username,
                "message": message,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "username": event["username"],
            "message": event["message"],
        }))

    @database_sync_to_async
    def user_can_access_course_chat(self, user_id: int, course_id: int) -> bool:
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return False

        # Teacher of the course can access
        if course.teacher_id == user_id:
            return True

        # Enrolled (not blocked) students can access
        return Enrollment.objects.filter(
            course_id=course_id,
            student_id=user_id,
            status=Enrollment.Status.ENROLLED,
        ).exists()