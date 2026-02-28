from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def home_router(request):
    if request.user.role == "TEACHER":
        return redirect("teacher_home")
    return redirect("student_home")


@login_required
def student_home(request):
    enrollments = request.user.course_enrollments.select_related("course")
    return render(request, "home_student.html", {
        "enrollments": enrollments,
    })


@login_required
def teacher_home(request):
    courses = request.user.courses_taught.all()
    return render(request, "home_teacher.html", {
        "courses": courses,
    })