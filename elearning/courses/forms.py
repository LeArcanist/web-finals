from django import forms
from .models import Course, CourseFeedback, CourseMaterial

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("title", "description")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class CourseFeedbackForm(forms.ModelForm):
    class Meta:
        model = CourseFeedback
        fields = ("rating", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),
        }

class CourseMaterialForm(forms.ModelForm):
    class Meta:
        model = CourseMaterial
        fields = ("title", "description", "file")        