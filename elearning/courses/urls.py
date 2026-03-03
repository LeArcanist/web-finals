from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_course, name="course_create"),
    path("", views.course_list, name="course_list"),
    path("<int:course_id>/", views.course_detail, name="course_detail"),
    path("<int:course_id>/enrol/", views.enrol_course, name="enrol_course"),
    path("<int:course_id>/manage/", views.teacher_course_manage, name="teacher_course_manage"),
]