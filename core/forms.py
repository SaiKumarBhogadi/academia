from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(
        choices=[(choice, label) for choice, label in User.USER_TYPE_CHOICES if choice != 'super_admin'],
        label="Register as"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    identifier = forms.CharField(max_length=255, label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)


class AdminAddUserForm(RegistrationForm):
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,  # Include all roles, including super_admin
        label="User Role"
    )
    is_approved = forms.BooleanField(
        required=False,
        label="Approve User",
        initial=True  # Default to approved for Super Admin
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type', 'is_approved']