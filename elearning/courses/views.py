from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Course, Enrollment


def _is_student(user) -> bool:
    return getattr(user, "role", None) == "STUDENT"


@login_required
def course_list(request):
    courses = Course.objects.select_related("teacher").all().order_by("title")

    enrolled_ids = set(
        Enrollment.objects.filter(student=request.user).values_list("course_id", flat=True)
    )

    return render(request, "courses/course_list.html", {
        "courses": courses,
        "enrolled_ids": enrolled_ids,
    })


@login_required
def course_detail(request, course_id: int):
    course = get_object_or_404(Course.objects.select_related("teacher"), pk=course_id)

    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()

    return render(request, "courses/course_detail.html", {
        "course": course,
        "enrollment": enrollment,
    })


@login_required
def enrol_course(request, course_id: int):
    if request.method != "POST":
        return HttpResponseForbidden("Enrol must be a POST request.")

    if not _is_student(request.user):
        return HttpResponseForbidden("Only students can enrol in courses.")

    course = get_object_or_404(Course, pk=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        course=course,
        student=request.user,
        defaults={"status": Enrollment.Status.ENROLLED},
    )

    if not created and enrollment.status == Enrollment.Status.BLOCKED:
        return HttpResponseForbidden("You are blocked from this course.")

    return redirect("course_detail", course_id=course.id)