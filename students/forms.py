from django import forms
from django.db import transaction
from core.models import User
from .models import StudentProfile
from colleges.utils import STATES_DISTRICTS

# Generate state choices dynamically
INDIAN_STATES = [(state, state) for state in STATES_DISTRICTS.keys()]

class StudentRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    state = forms.ChoiceField(
        choices=INDIAN_STATES,
        widget=forms.Select(attrs={'id': 'id_state', 'class': 'form-control'})
    )
    district = forms.ChoiceField(
        choices=[('', 'Select District')],
        widget=forms.Select(attrs={'id': 'id_district', 'class': 'form-control'})
    )

    class Meta:
        model = StudentProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_photo',
            'nationality', 'category', 'aadhar_number', 'email', 'contact_number',
            'alternate_phone_number', 'street_address', 'city', 'state', 'district',
            'pincode', 'father_name', 'father_mobile', 'father_email', 'mother_name',
            'mother_mobile', 'mother_email', 'parent_income', 'admission_preference',
            'desired_course', 'last_institution', 'previous_qualification', 'marksheet',
            'transfer_certificate', 'entrance_score', 'academic_year', 'id_proof',
            'caste_certificate', 'income_certificate', 'passport_photo', 'signature'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'aadhar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'father_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'admission_preference': forms.Select(attrs={'class': 'form-select'}),
            'desired_course': forms.TextInput(attrs={'class': 'form-control'}),
            'last_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'marksheet': forms.FileInput(attrs={'class': 'form-control'}),
            'transfer_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'entrance_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'id_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'caste_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'income_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update district choices based on the selected state
        if 'state' in self.data:
            state = self.data.get('state')
            if state in STATES_DISTRICTS:
                self.fields['district'].choices = [('', 'Select District')] + [(district, district) for district in STATES_DISTRICTS[state]]
            else:
                self.fields['district'].choices = [('', 'Select District')]
        else:
            self.fields['district'].choices = [('', 'Select District')]
        # Set optional fields
        self.fields['income_certificate'].required = False
        self.fields['profile_photo'].required = True
        self.fields['aadhar_number'].required = True
        self.fields['alternate_phone_number'].required = False
        self.fields['father_email'].required = False
        self.fields['mother_email'].required = False
        self.fields['parent_income'].required = False
        self.fields['marksheet'].required = True
        self.fields['transfer_certificate'].required = True
        self.fields['entrance_score'].required = False
        self.fields['id_proof'].required = True
        self.fields['caste_certificate'].required = False
        self.fields['passport_photo'].required = True
        self.fields['signature'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Username is required.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def clean_contact_number(self):
        phone = self.cleaned_data.get('contact_number')
        if not phone:
            raise forms.ValidationError("Contact number is required.")
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Contact number must be a 10-digit number.")
        return phone

    def clean_alternate_phone_number(self):
        phone = self.cleaned_data.get('alternate_phone_number')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Alternate phone number must be a 10-digit number.")
        return phone

    def clean_father_mobile(self):
        phone = self.cleaned_data.get('father_mobile')
        if not phone:
            raise forms.ValidationError("Father's mobile number is required.")
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Father's mobile number must be a 10-digit number.")
        return phone

    def clean_mother_mobile(self):
        phone = self.cleaned_data.get('mother_mobile')
        if not phone:
            raise forms.ValidationError("Mother's mobile number is required.")
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Mother's mobile number must be a 10-digit number.")
        return phone

    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number')
        if aadhar and (not aadhar.isdigit() or len(aadhar) != 12):
            raise forms.ValidationError("Aadhar number must be a 12-digit number.")
        return aadhar

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        state = cleaned_data.get('state')
        district = cleaned_data.get('district')

        if not password:
            raise forms.ValidationError("Password is required.")
        if not confirm_password:
            raise forms.ValidationError("Confirm password is required.")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        if not state:
            raise forms.ValidationError("State is required.")
        if not district:
            raise forms.ValidationError("District is required.")
        if district not in STATES_DISTRICTS.get(state, []):
            raise forms.ValidationError("Invalid district for the selected state.")

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            user = User(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                user_type='student',
                is_approved=False
            )
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
                profile = super().save(commit=False)
                profile.user = user
                profile.save()
            return user

class StudentProfileForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=INDIAN_STATES,
        widget=forms.Select(attrs={'id': 'id_state', 'class': 'form-control'})
    )
    district = forms.ChoiceField(
        choices=[('', 'Select District')],
        widget=forms.Select(attrs={'id': 'id_district', 'class': 'form-control'})
    )

    class Meta:
        model = StudentProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender', 'profile_photo',
            'nationality', 'category', 'aadhar_number', 'email', 'contact_number',
            'alternate_phone_number', 'street_address', 'city', 'state', 'district',
            'pincode', 'father_name', 'father_mobile', 'father_email', 'mother_name',
            'mother_mobile', 'mother_email', 'parent_income', 'admission_preference',
            'desired_course', 'last_institution', 'previous_qualification', 'marksheet',
            'transfer_certificate', 'entrance_score', 'academic_year', 'id_proof',
            'caste_certificate', 'income_certificate', 'passport_photo', 'signature'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'aadhar_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'father_name': forms.TextInput(attrs={'class': 'form-control'}),
            'father_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'father_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mother_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'mother_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'parent_income': forms.NumberInput(attrs={'class': 'form-control'}),
            'admission_preference': forms.Select(attrs={'class': 'form-select'}),
            'desired_course': forms.TextInput(attrs={'class': 'form-control'}),
            'last_institution': forms.TextInput(attrs={'class': 'form-control'}),
            'previous_qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'marksheet': forms.FileInput(attrs={'class': 'form-control'}),
            'transfer_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'entrance_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'id_proof': forms.FileInput(attrs={'class': 'form-control'}),
            'caste_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'income_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'signature': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update district choices based on the selected state
        if 'state' in self.data:
            state = self.data.get('state')
            if state in STATES_DISTRICTS:
                self.fields['district'].choices = [('', 'Select District')] + [(district, district) for district in STATES_DISTRICTS[state]]
            else:
                self.fields['district'].choices = [('', 'Select District')]
        elif self.instance and self.instance.state:
            state = self.instance.state
            if state in STATES_DISTRICTS:
                self.fields['district'].choices = [('', 'Select District')] + [(district, district) for district in STATES_DISTRICTS[state]]
        else:
            self.fields['district'].choices = [('', 'Select District')]
        # Set optional fields
        self.fields['income_certificate'].required = False
        self.fields['profile_photo'].required = False
        self.fields['aadhar_number'].required = True
        self.fields['alternate_phone_number'].required = False
        self.fields['father_email'].required = False
        self.fields['mother_email'].required = False
        self.fields['parent_income'].required = False
        self.fields['marksheet'].required = True
        self.fields['transfer_certificate'].required = True
        self.fields['entrance_score'].required = False
        self.fields['id_proof'].required = True
        self.fields['caste_certificate'].required = False
        self.fields['passport_photo'].required = True
        self.fields['signature'].required = True

    def clean_contact_number(self):
        phone = self.cleaned_data.get('contact_number')
        if not phone:
            raise forms.ValidationError("Contact number is required.")
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Contact number must be a 10-digit number.")
        return phone

    def clean_alternate_phone_number(self):
        phone = self.cleaned_data.get('alternate_phone_number')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Alternate phone number must be a 10-digit number.")
        return phone

    def clean_father_mobile(self):
        phone = self.cleaned_data.get('father_mobile')
        if not phone:
            raise forms.ValidationError("Father's mobile number is required.")
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Father's mobile number must be a 10-digit number.")
        return phone

    def clean_mother_mobile(self):
        phone = self.cleaned_data.get('mother_mobile')
        if not phone:
            raise forms.ValidationError("Mother's mobile number is required.")
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Mother's mobile number must be a 10-digit number.")
        return phone

    def clean_aadhar_number(self):
        aadhar = self.cleaned_data.get('aadhar_number')
        if aadhar and (not aadhar.isdigit() or len(aadhar) != 12):
            raise forms.ValidationError("Aadhar number must be a 12-digit number.")
        return aadhar

    def clean(self):
        cleaned_data = super().clean()
        state = cleaned_data.get('state')
        district = cleaned_data.get('district')

        if not state:
            raise forms.ValidationError("State is required.")
        if not district:
            raise forms.ValidationError("District is required.")
        if district not in STATES_DISTRICTS.get(state, []):
            raise forms.ValidationError("Invalid district for the selected state.")

        return cleaned_data