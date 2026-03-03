from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment
from realtime.models import Notification


@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrolment(sender, instance: Enrollment, created: bool, **kwargs):
    if not created:
        return

    course = instance.course
    student = instance.student
    teacher = course.teacher

    Notification.objects.create(
        recipient=teacher,
        message=f"{student.username} enrolled in {course.title}.",
        link=f"/courses/{course.id}/manage/",
    )