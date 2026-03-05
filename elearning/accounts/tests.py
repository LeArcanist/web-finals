from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="s1", password="pass12345", role="STUDENT"
        )

    def test_login_page_redirects_if_authenticated(self):
        
        self.client.login(username="s1", password="pass12345")
        resp = self.client.get(reverse("login")) 
        self.assertIn(resp.status_code, (302, 303))

    def test_user_directory_requires_login(self):
        resp = self.client.get(reverse("user_directory"))
        self.assertIn(resp.status_code, (302, 303))
        self.assertIn("?next=", resp["Location"])