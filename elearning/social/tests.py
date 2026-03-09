from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from social.models import StatusUpdate

User = get_user_model()

class SocialStatusTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="s1", password="pass12345", role="STUDENT"
        )

    def test_student_can_post_status_update(self):
        self.client.login(username="s1", password="pass12345")

        resp = self.client.post(
            reverse("student_home"), 
            data={"action": "post_status", "content": "Hello world"},
        )
        self.assertIn(resp.status_code, (302, 303))
        self.assertTrue(StatusUpdate.objects.filter(author=self.student, content="Hello world").exists())