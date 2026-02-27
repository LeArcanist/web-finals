from django.contrib import admin
from .models import Course, Enrollment, CourseMaterial, CourseFeedback


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "created_at")
    search_fields = ("title", "teacher__username", "teacher__email")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("course__title", "student__username", "student__email")


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "uploaded_by", "uploaded_at")
    search_fields = ("title", "course__title", "uploaded_by__username")


@admin.register(CourseFeedback)
class CourseFeedbackAdmin(admin.ModelAdmin):
    list_display = ("course", "student", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("course__title", "student__username")