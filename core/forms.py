from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    user_type = forms.ChoiceField(
        choices=[(choice, label) for choice, label in User.USER_TYPE_CHOICES if choice != 'super_admin'],
        label="Register as"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance.pk:
            # Exclude current instance from uniqueness check during edit
            if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("A user with that username already exists.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance.pk:
            # Exclude current instance from uniqueness check during edit
            if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("A user with that email already exists.")
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password or confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
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
        fields = ['username', 'email', 'password', 'confirm_password', 'user_type', 'is_approved']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
            'confirm_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password and confirm_password optional in edit mode
        if self.instance.pk:
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
            # Add a note about password not being shown
            self.fields['password'].help_text = "Leave blank to keep the current password. (Current password not shown for security)"
            self.fields['confirm_password'].help_text = "Required only if changing password."

    # Inherit clean methods from RegistrationForm, which handle edit mode