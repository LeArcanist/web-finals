import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import DirectMessage
from realtime.models import Notification

from django.contrib.auth import get_user_model
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
    
User = get_user_model()

class DirectMessageConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def save_message_and_notify(self, sender_id: int, recipient_id: int, msg: str):
        DirectMessage.objects.create(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=msg,
        )
        Notification.objects.create(
            recipient_id=recipient_id,
            message=f"New message from {self.user.username}",
            link=f"/dm/{sender_id}/",
        )

    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_user_id = int(self.scope["url_route"]["kwargs"]["other_user_id"])

        # Ensure other user exists
        other_exists = await self.user_exists(self.other_user_id)
        if not other_exists:
            await self.close()
            return

        a, b = sorted([self.user.id, self.other_user_id])
        self.room_group_name = f"dm_{a}_{b}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send last 30 messages as history
        history = await self.get_history(a, b, limit=30)
        await self.send(text_data=json.dumps({"type": "history", "messages": history}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg = (data.get("message") or "").strip()
        if not msg:
            return

        # Save to DB
        await self.save_message_and_notify(self.user.id, self.other_user_id, msg)
        await self.channel_layer.group_send(
        f"user_{self.other_user_id}",
            {
                "type": "notify",
                "message": f"New message from {self.user.username}",
                "link": f"/dm/{self.user.id}/",
                "created_at": "",   # optional
                "is_read": False,
            }
        )
        # Broadcast to both participants
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "dm.message",
                "sender_id": self.user.id,
                "sender_username": self.user.username,
                "message": msg,
            }
        )

    async def dm_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "sender_id": event["sender_id"],
            "sender_username": event["sender_username"],
            "message": event["message"],
        }))

    @database_sync_to_async
    def user_exists(self, user_id: int) -> bool:
        return User.objects.filter(id=user_id).exists()

    @database_sync_to_async
    def save_message(self, sender_id: int, recipient_id: int, msg: str):
        DirectMessage.objects.create(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message=msg,
        )

    @database_sync_to_async
    def get_history(self, a: int, b: int, limit: int = 30):
        qs = DirectMessage.objects.filter(
            sender_id__in=[a, b],
            recipient_id__in=[a, b],
        ).order_by("-created_at")[:limit]
        items = list(reversed(list(qs.values("sender_id", "message", "created_at"))))
        # Convert datetime to string for JSON
        for it in items:
            it["created_at"] = it["created_at"].isoformat(sep=" ", timespec="seconds")
        return items

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        # event payload becomes JSON to browser
        await self.send(text_data=json.dumps({
            "type": "notification",
            "message": event["message"],
            "link": event.get("link", ""),
            "created_at": event.get("created_at", ""),
            "is_read": event.get("is_read", False),
        }))