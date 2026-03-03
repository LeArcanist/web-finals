from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Course, Enrollment, CourseFeedback, CourseMaterial
from .forms import CourseFeedbackForm, CourseForm, CourseMaterialForm

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
    is_enrolled = enrollment is not None and enrollment.status == Enrollment.Status.ENROLLED

    # Lists to display
    materials = CourseMaterial.objects.filter(course=course).order_by("-uploaded_at")
    feedback_list = CourseFeedback.objects.filter(course=course).select_related("student").order_by("-created_at")

    # --- Teacher upload logic ---
    is_course_teacher = _is_teacher(request.user) and (course.teacher_id == request.user.id)
    material_form = None

    # --- Student feedback logic ---
    existing_feedback = None
    can_leave_feedback = False
    feedback_form = None

    # Handle POST actions with a hidden "action" field
    if request.method == "POST":
        action = request.POST.get("action")

        # Teacher uploads a material
        if action == "upload_material":
            if not is_course_teacher:
                return HttpResponseForbidden("Only the teacher of this course can upload materials.")

            material_form = CourseMaterialForm(request.POST, request.FILES)
            if material_form.is_valid():
                m = material_form.save(commit=False)
                m.course = course
                m.uploaded_by = request.user
                m.save()
                return redirect("course_detail", course_id=course.id)

        # Student submits feedback
        elif action == "submit_feedback":
            if not (_is_student(request.user) and is_enrolled):
                return HttpResponseForbidden("Only enrolled students can leave feedback.")

            existing_feedback = CourseFeedback.objects.filter(course=course, student=request.user).first()
            if existing_feedback:
                return HttpResponseForbidden("You have already left feedback for this course.")

            feedback_form = CourseFeedbackForm(request.POST)
            if feedback_form.is_valid():
                fb = feedback_form.save(commit=False)
                fb.course = course
                fb.student = request.user
                fb.save()
                return redirect("course_detail", course_id=course.id)

        else:
            return HttpResponseForbidden("Invalid action.")

    # If GET (or POST failed validation), build forms for display
    if is_course_teacher and material_form is None:
        material_form = CourseMaterialForm()

    if _is_student(request.user) and is_enrolled:
        existing_feedback = CourseFeedback.objects.filter(course=course, student=request.user).first()
        can_leave_feedback = existing_feedback is None
        if can_leave_feedback and feedback_form is None:
            feedback_form = CourseFeedbackForm()

    return render(request, "courses/course_detail.html", {
        "course": course,
        "enrollment": enrollment,
        "materials": materials,

        "is_course_teacher": is_course_teacher,
        "material_form": material_form,

        "feedback_list": feedback_list,
        "existing_feedback": existing_feedback,
        "can_leave_feedback": can_leave_feedback,
        "feedback_form": feedback_form,
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

def _is_teacher(user) -> bool:
    return getattr(user, "role", None) == "TEACHER"


@login_required
def create_course(request):
    if not _is_teacher(request.user):
        return HttpResponseForbidden("Teachers only.")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect("course_detail", course_id=course.id)
    else:
        form = CourseForm()

    return render(request, "courses/course_create.html", {"form": form})

@login_required
def teacher_course_manage(request, course_id: int):
    course = get_object_or_404(Course.objects.select_related("teacher"), pk=course_id)

    # Only the teacher who owns this course can manage it
    if not _is_teacher(request.user) or course.teacher_id != request.user.id:
        return HttpResponseForbidden("Only the teacher of this course can view this page.")

    enrollments = (
        Enrollment.objects
        .filter(course=course)
        .select_related("student")
        .order_by("student__username")
    )

    return render(request, "courses/teacher_course_manage.html", {
        "course": course,
        "enrollments": enrollments,
    })