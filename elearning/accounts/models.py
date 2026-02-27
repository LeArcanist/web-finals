from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    real_name = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)