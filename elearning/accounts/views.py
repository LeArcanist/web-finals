from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import User

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

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})

@login_required
def teacher_search(request):
    if request.user.role != "TEACHER":
        return HttpResponseForbidden("Teachers only.")

    q = (request.GET.get("q") or "").strip()

    students = User.objects.none()
    teachers = User.objects.none()

    if q:
        base_filter = (
            Q(username__icontains=q)
            | Q(real_name__icontains=q)
            | Q(email__icontains=q)
        )

        students = User.objects.filter(base_filter, role="STUDENT").order_by("username")[:50]
        teachers = User.objects.filter(base_filter, role="TEACHER").order_by("username")[:50]

    return render(request, "accounts/teacher_search.html", {
        "q": q,
        "students": students,
        "teachers": teachers,
    })