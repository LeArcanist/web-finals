from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "real_name",
            "role",
            "photo",
            "password1",
            "password2",
        )

    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter username",
        })
        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter email",
        })
        self.fields["real_name"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter your real name",
        })
        self.fields["role"].widget.attrs.update({
            "class": "form-control",
        })
        self.fields["photo"].widget.attrs.update({
            "class": "form-control",
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter password",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password",
        })

        self.fields["password1"].help_text = ""
        self.fields["password2"].help_text = ""
        self.fields["username"].help_text = ""