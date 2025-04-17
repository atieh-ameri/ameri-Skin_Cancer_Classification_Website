from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


# User Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

# User Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": "form-control"}))


from .models import ImageUpload

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ["sex", "dob", "location", "image"]
        widgets = {
            "sex": forms.Select(attrs={"class": "form-control"}),
            "dob": forms.Select(attrs={"class": "form-control"}),
            "location": forms.Select(attrs={"class": "form-control", "placeholder": "Enter location"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control-file", "onchange": "previewImage(event)"}),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=300, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You can add custom email validation here if needed
        return email


