from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import User, Profile

validate_username = RegexValidator(r"^[a-zA-Z][a-zA-Z0-9_]{3,14}$",
    "Usernames must start with a letter and be between 4-15 alphanumeric characters in length")

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=15, validators=[validate_username])
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(min_length=8, widget=forms.PasswordInput())
    password_confirm = forms.CharField(min_length=8, widget=forms.PasswordInput())
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        clean_data = super().clean()
        if clean_data['password'] != clean_data['password_confirm']:
            self.add_error('password_confirm', "Passwords entered do not match")
        return clean_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio',)


class AddCommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea)
