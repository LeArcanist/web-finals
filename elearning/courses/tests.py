from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

from courses.models import Course, Enrollment, CourseMaterial, CourseFeedback
from realtime.models import Notification

User = get_user_model()

class CourseFlowsTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="t1", password="pass12345", role="TEACHER"
        )
        self.student = User.objects.create_user(
            username="s1", password="pass12345", role="STUDENT"
        )
        self.course = Course.objects.create(
            title="Math 101",
            description="Intro",
            teacher=self.teacher,
        )

    def test_student_can_enroll(self):
        self.client.login(username="s1", password="pass12345")
        resp = self.client.post(reverse("enrol_course", args=[self.course.id]))
        self.assertIn(resp.status_code, (302, 303))

        e = Enrollment.objects.get(course=self.course, student=self.student)
        self.assertEqual(e.status, Enrollment.Status.ENROLLED)

    def test_blocked_student_cannot_enroll(self):
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.BLOCKED)

        self.client.login(username="s1", password="pass12345")
        resp = self.client.post(reverse("enrol_course", args=[self.course.id]))
        self.assertEqual(resp.status_code, 403)

        e = Enrollment.objects.get(course=self.course, student=self.student)
        self.assertEqual(e.status, Enrollment.Status.BLOCKED)

    def test_only_teacher_can_upload_material(self):
        self.client.login(username="s1", password="pass12345")
        upload = SimpleUploadedFile("test.txt", b"hello", content_type="text/plain")
        resp = self.client.post(
            reverse("course_detail", args=[self.course.id]),
            data={"action": "upload_material", "title": "File1", "description": "d", "file": upload},
        )
        self.assertEqual(resp.status_code, 403)

        self.client.login(username="t1", password="pass12345")
        upload2 = SimpleUploadedFile("test2.txt", b"hello2", content_type="text/plain")
        resp2 = self.client.post(
            reverse("course_detail", args=[self.course.id]),
            data={"action": "upload_material", "title": "File2", "description": "d", "file": upload2},
        )
        self.assertIn(resp2.status_code, (302, 303))
        self.assertTrue(CourseMaterial.objects.filter(course=self.course, title="File2").exists())

    def test_materials_visibility_requires_enrolled_or_teacher(self):
        # create material
        CourseMaterial.objects.create(
            course=self.course,
            uploaded_by=self.teacher,
            title="Slides",
            description="Week1",
            file=SimpleUploadedFile("slides.txt", b"content"),
        )

        # student not enrolled: should not see
        self.client.login(username="s1", password="pass12345")
        resp = self.client.get(reverse("course_detail", args=[self.course.id]))
        self.assertNotContains(resp, "Slides")

        # enroll student: should see
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.ENROLLED)
        resp2 = self.client.get(reverse("course_detail", args=[self.course.id]))
        self.assertContains(resp2, "Slides")

        # teacher: should see
        self.client.login(username="t1", password="pass12345")
        resp3 = self.client.get(reverse("course_detail", args=[self.course.id]))
        self.assertContains(resp3, "Slides")

    def test_feedback_only_once_and_only_enrolled(self):
        self.client.login(username="s1", password="pass12345")

        # not enrolled = forbidden
        resp = self.client.post(
            reverse("course_detail", args=[self.course.id]),
            data={"action": "submit_feedback", "rating": 5, "comment": "Great"},
        )
        self.assertEqual(resp.status_code, 403)

        # enrolled = ok
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.ENROLLED)
        resp2 = self.client.post(
            reverse("course_detail", args=[self.course.id]),
            data={"action": "submit_feedback", "rating": 5, "comment": "Great"},
        )
        self.assertIn(resp2.status_code, (302, 303))
        self.assertEqual(CourseFeedback.objects.filter(course=self.course, student=self.student).count(), 1)

        # second feedback => forbidden
        resp3 = self.client.post(
            reverse("course_detail", args=[self.course.id]),
            data={"action": "submit_feedback", "rating": 4, "comment": "Again"},
        )
        self.assertEqual(resp3.status_code, 403)

    def test_remove_student_blocks_and_notifies(self):
        Enrollment.objects.create(course=self.course, student=self.student, status=Enrollment.Status.ENROLLED)

        self.client.login(username="t1", password="pass12345")
        resp = self.client.post(reverse("remove_student", args=[self.course.id, self.student.id]))
        self.assertIn(resp.status_code, (302, 303))

        e = Enrollment.objects.get(course=self.course, student=self.student)
        self.assertEqual(e.status, Enrollment.Status.BLOCKED)

        self.assertTrue(Notification.objects.filter(recipient=self.student, message__icontains="removed").exists())