from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_course, name="course_create"),
    path("", views.course_list, name="course_list"),
    path("<int:course_id>/", views.course_detail, name="course_detail"),
    path("<int:course_id>/enrol/", views.enrol_course, name="enrol_course"),
    path("<int:course_id>/manage/", views.teacher_course_manage, name="teacher_course_manage"),
    path("<int:course_id>/chat/", views.course_chat, name="course_chat"),
    path("<int:course_id>/remove/<int:student_id>/", views.remove_student, name="remove_student"),
    path("<int:course_id>/unblock/<int:student_id>/", views.unblock_student, name="unblock_student"),
    path("materials/<int:material_id>/delete/", views.delete_material, name="delete_material"),
]