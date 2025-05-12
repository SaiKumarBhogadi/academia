from django import forms
from .models import User

class LoginForm(forms.Form):
    identifier = forms.CharField(max_length=255, label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)

class AdminAddUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", required=False)
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        label="User Role"
    )
    is_approved = forms.BooleanField(
        required=False,
        label="Approve User",
        initial=True
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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance.pk:
            if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise forms.ValidationError("A user with that username already exists.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance.pk:
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
    






from django import forms
import os
import json
from django.conf import settings
from schools.models import SchoolProfile
from colleges.models import CollegeProfile

class InstitutionSelectionForm(forms.Form):
    state = forms.ChoiceField(choices=[('', 'Select State')], required=False)
    district = forms.ChoiceField(choices=[('', 'Select District')], required=False)
    institution_type = forms.ChoiceField(
        choices=[
            ('', 'Select Institution Type'),
            ('school', 'School'),
            ('college', 'College')
        ],
        required=False
    )
    institution = forms.ChoiceField(choices=[('', 'Select Institution')], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate state choices from JSON
        json_path = os.path.join(settings.BASE_DIR, 'data/indian_states_districts.json')
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            states = sorted(data.keys())
            self.fields['state'].choices = [('', 'Select State')] + [(state, state) for state in states]
        except Exception as e:
            self.fields['state'].choices = [('', 'Select State')]

        # Dynamically populate district choices based on state
        if 'state' in self.data and self.data['state']:
            state = self.data['state']
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                if state in data:
                    districts = sorted(data[state])
                    self.fields['district'].choices = [('', 'Select District')] + [(district, district) for district in districts]
            except Exception as e:
                self.fields['district'].choices = [('', 'Select District')]

        # Dynamically populate institution choices based on district and institution_type
        if 'district' in self.data and 'institution_type' in self.data:
            district = self.data['district']
            institution_type = self.data['institution_type']
            institutions = []
            if district and institution_type:
                if institution_type == 'school':
                    schools = SchoolProfile.objects.filter(user__is_approved=True, district__iexact=district)
                    institutions = [(f'school_{school.id}', f'{school.school_name} ({school.board_affiliation})') for school in schools]
                elif institution_type == 'college':
                    colleges = CollegeProfile.objects.filter(user__is_approved=True, district__iexact=district)
                    institutions = [(f'college_{college.id}', f'{college.college_name}') for college in colleges]
            self.fields['institution'].choices = [('', 'Select Institution')] + institutions

from django import forms

from django import forms

class OnlineAdmissionForm(forms.Form):
    # Category 1: Application Information
    email = forms.EmailField(label="Email Address")
    desired_course = forms.CharField(max_length=100, label="Desired Course/Grade", required=False)

    # Category 2: Personal Information
    first_name = forms.CharField(max_length=50, label="First Name")
    middle_name = forms.CharField(max_length=50, label="Middle Name", required=False)
    last_name = forms.CharField(max_length=50, label="Last Name")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Date of Birth")
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], label="Gender")
    nationality = forms.CharField(max_length=50, label="Nationality", initial="Indian")
    aadhaar_number = forms.CharField(max_length=12, label="Aadhaar Number", required=False)
    contact_number = forms.CharField(max_length=10, label="Student Contact Number", required=False)
    permanent_address = forms.CharField(widget=forms.Textarea, label="Permanent Address")
    correspondence_address = forms.CharField(widget=forms.Textarea, label="Correspondence Address", required=False)
    caste = forms.CharField(max_length=20, label="Caste", required=False)
    religion = forms.CharField(max_length=20, label="Religion", required=False)
    mother_tongue = forms.CharField(max_length=50, label="Mother Tongue", required=False)
    blood_group = forms.CharField(max_length=3, label="Blood Group", required=False)
    city = forms.CharField(max_length=100, label="City")
    state = forms.CharField(max_length=100, label="State")
    pincode = forms.CharField(max_length=6, label="Pincode")

    # Category 3: Parent Information
    father_name = forms.CharField(max_length=255, label="Father's Name")
    father_occupation = forms.CharField(max_length=100, label="Father's Occupation", required=False)
    father_mobile = forms.CharField(max_length=10, label="Father's Contact Number")
    father_email = forms.EmailField(label="Father's Email", required=False)
    mother_name = forms.CharField(max_length=255, label="Mother's Name")
    mother_occupation = forms.CharField(max_length=100, label="Mother's Occupation", required=False)
    mother_mobile = forms.CharField(max_length=10, label="Mother's Contact Number")
    mother_email = forms.EmailField(label="Mother's Email", required=False)
    parent_income = forms.DecimalField(max_digits=10, decimal_places=2, label="Parent Income", required=False)

    # Category 4: Academic Information
    last_institution = forms.CharField(max_length=200, label="Previous Institution Name")
    previous_school_address = forms.CharField(widget=forms.Textarea, label="Previous Institution Address", required=False)
    previous_qualification = forms.CharField(max_length=20, label="Class Last Attended/Qualification")
    board = forms.ChoiceField(choices=[('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('State Board', 'State Board'), ('Other', 'Other')], label="Board of Education")
    year_of_passing = forms.IntegerField(label="Year of Passing")
    percentage = forms.FloatField(label="Percentage Obtained")
    entrance_score = forms.FloatField(label="Entrance Score", required=False)
    reason_for_leaving = forms.CharField(widget=forms.Textarea, label="Reason for Leaving", required=False)

    # Category 5: Documents
    birth_certificate = forms.FileField(label="Birth Certificate")
    id_proof = forms.FileField(label="ID Proof", required=False)
    caste_certificate = forms.FileField(label="Caste Certificate", required=False)
    marksheet = forms.FileField(label="Previous Mark Sheet")
    transfer_certificate = forms.FileField(label="Transfer Certificate")
    passport_photo = forms.FileField(label="Passport Size Photo")
    address_proof = forms.FileField(label="Address Proof")
    income_certificate = forms.FileField(label="Income Certificate", required=False)

    def __init__(self, *args, institution_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        if institution_type == 'college':
            self.fields['desired_course'].required = True



from django import forms
from core.models import User

class UserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
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
    


from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()  # ✅ Correct way to reference the CustomUser model

class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No account found with this email.")
        return email