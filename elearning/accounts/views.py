from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import User

from social.forms import StatusUpdateForm
from social.models import StatusUpdate

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileUpdateForm


@login_required
def home_router(request):
    if request.user.role == "TEACHER":
        return redirect("teacher_home")
    return redirect("student_home")


@login_required
def student_home(request):
    enrollments = request.user.course_enrollments.select_related("course")

    # status posting
    form = StatusUpdateForm()
    if request.method == "POST" and request.POST.get("action") == "post_status":
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            s = form.save(commit=False)
            s.author = request.user
            s.save()
            return redirect("home")

    # show latest 20 updates
    status_updates = StatusUpdate.objects.filter(author=request.user)[:20]

    return render(request, "home_student.html", {
        "enrollments": enrollments,
        "status_form": form,
        "status_updates": status_updates,
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

@login_required
def dm_chat(request, user_id: int):
    other = get_object_or_404(User, id=user_id)
    return render(request, "accounts/dm_chat.html", {"other": other})

@login_required
def user_directory(request):
    q = (request.GET.get("q") or "").strip()

    users = User.objects.all().order_by("username")

    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(real_name__icontains=q) |
            Q(email__icontains=q)
        ).order_by("username")

    users = users.exclude(id=request.user.id)[:100]

    return render(request, "accounts/user_directory.html", {
        "q": q,
        "users": users,
    })

# updating profile
@login_required
def profile_view(request):
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_profile":
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            password_form = PasswordChangeForm(user=request.user)

            if profile_form.is_valid():
                profile_form.save()
                return redirect("profile")

        elif action == "change_password":
            profile_form = ProfileUpdateForm(instance=request.user)
            password_form = PasswordChangeForm(user=request.user, data=request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect("profile")

    return render(request, "profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
    })