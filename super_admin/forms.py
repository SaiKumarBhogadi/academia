from django import forms

class UserTypeSelectionForm(forms.Form):
    user_type = forms.ChoiceField(
        choices=[
            ('', 'Select User Type'),
            ('college', 'College'),
            ('school', 'School'),
            ('student', 'Student'),
        ],
        label="User Type",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_user_type'}),
    )




from django import forms
from core.models import User

class UserEditForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # Get the request object to check the user
        super().__init__(*args, **kwargs)
        # Restrict email field for non-super admin users
        if self.request and self.request.user.user_type != 'super_admin':
            self.fields['email'].widget.attrs['readonly'] = True  # Make email read-only for non-super admins

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        # Prevent email updates for non-super admin users
        if self.request and self.request.user.user_type != 'super_admin':
            if self.instance.email != cleaned_data.get('email'):
                raise forms.ValidationError("Only super admins can update the email.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user