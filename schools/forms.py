from django import forms
from .models import SchoolProfile
from django.db import transaction

from django import forms
from django.db import transaction
from core.models import User
from .models import SchoolProfile
from colleges.utils import STATES_DISTRICTS

# Generate state choices dynamically
INDIAN_STATES = [(state, state) for state in STATES_DISTRICTS.keys()]
INDIAN_STATES.insert(0, ('', 'Select State'))

class SchoolRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Username")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    state = forms.ChoiceField(
        choices=INDIAN_STATES,
        required=False,
        widget=forms.Select(attrs={'id': 'id_state', 'class': 'form-control'})
    )
    district = forms.ChoiceField(
        choices=[('', 'Select District')],
        required=False,
        widget=forms.Select(attrs={'id': 'id_district', 'class': 'form-control'})
    )

    class Meta:
        model = SchoolProfile
        fields = [
            'school_name', 'principal_name', 'contact_phone', 'alternate_phone_number', 'contact_email',
            'school_type', 'board_affiliation', 'medium_of_instruction', 'established_year',
            'total_students', 'total_teachers', 'school_code', 'street_address', 'city', 'state',
            'district', 'pincode', 'website', 'logo', 'affiliation_certificate', 'brochure'
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'school_type': forms.Select(attrs={'class': 'form-select'}),
            'board_affiliation': forms.Select(attrs={'class': 'form-select'}),
            'medium_of_instruction': forms.Select(attrs={'class': 'form-select'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2025}),
            'total_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_teachers': forms.NumberInput(attrs={'class': 'form-control'}),
            'school_code': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'affiliation_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'brochure': forms.FileInput(attrs={'class': 'form-control'}),
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

    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Contact phone must be a 10-digit number.")
        return phone

    def clean_alternate_phone_number(self):
        phone = self.cleaned_data.get('alternate_phone_number')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Alternate phone must be a 10-digit number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        state = cleaned_data.get('state')
        district = cleaned_data.get('district')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # Validate district based on state
        if state and district:
            if district not in STATES_DISTRICTS.get(state, []):
                raise forms.ValidationError("Invalid district for the selected state.")
        elif state and not district:
            raise forms.ValidationError("Please select a district.")
        elif district and not state:
            raise forms.ValidationError("Please select a state before selecting a district.")

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            user = User(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                user_type='school',
                is_approved=False
            )
            user.set_password(self.cleaned_data['password'])
            if commit:
                user.save()
                profile = super().save(commit=False)
                profile.user = user
                profile.save()
            return user

class SchoolProfileForm(forms.ModelForm):
    state = forms.ChoiceField(
        choices=INDIAN_STATES,
        required=False,
        widget=forms.Select(attrs={'id': 'id_state', 'class': 'form-control'})
    )
    district = forms.ChoiceField(
        choices=[('', 'Select District')],
        required=False,
        widget=forms.Select(attrs={'id': 'id_district', 'class': 'form-control'})
    )

    class Meta:
        model = SchoolProfile
        fields = [
            'school_name', 'principal_name', 'contact_phone', 'alternate_phone_number', 'contact_email',
            'school_type', 'board_affiliation', 'medium_of_instruction', 'established_year',
            'total_students', 'total_teachers', 'school_code', 'street_address', 'city', 'state',
            'district', 'pincode', 'website', 'logo', 'affiliation_certificate', 'brochure'
        ]
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'alternate_phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'school_type': forms.Select(attrs={'class': 'form-select'}),
            'board_affiliation': forms.Select(attrs={'class': 'form-select'}),
            'medium_of_instruction': forms.Select(attrs={'class': 'form-select'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2025}),
            'total_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_teachers': forms.NumberInput(attrs={'class': 'form-control'}),
            'school_code': forms.TextInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'affiliation_certificate': forms.FileInput(attrs={'class': 'form-control'}),
            'brochure': forms.FileInput(attrs={'class': 'form-control'}),
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

    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Contact phone must be a 10-digit number.")
        return phone

    def clean_alternate_phone_number(self):
        phone = self.cleaned_data.get('alternate_phone_number')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Alternate phone must be a 10-digit number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        state = cleaned_data.get('state')
        district = cleaned_data.get('district')

        # Validate district based on state
        if state and district:
            if district not in STATES_DISTRICTS.get(state, []):
                raise forms.ValidationError("Invalid district for the selected state.")
        elif state and not district:
            raise forms.ValidationError("Please select a district.")
        elif district and not state:
            raise forms.ValidationError("Please select a state before selecting a district.")

        return cleaned_data

from django import forms
from .models import SchoolClass, ClassSection, AdmissionCycle  # Added AdmissionCycle

class SchoolClassForm(forms.ModelForm):
    cycle = forms.ModelChoiceField(queryset=AdmissionCycle.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = SchoolClass
        fields = ['grade', 'total_sections', 'cycle']  # Added cycle
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grade 1'}),
            'total_sections': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class ClassSectionForm(forms.ModelForm):
    cycle = forms.ModelChoiceField(queryset=AdmissionCycle.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ClassSection
        fields = ['section_name', 'total_seats', 'cycle']  # Added cycle
        widgets = {
            'section_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Section A'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


from django import forms
from core.models import User  # Import User from core.models
from .models import SchoolClass, ClassSection, Admission, AdmissionCycle  # Added AdmissionCycle

class AdmissionForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(user_type='student'), widget=forms.Select(attrs={'class': 'form-control'}))
    cycle = forms.ModelChoiceField(queryset=AdmissionCycle.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))  # Added cycle

    class Meta:
        model = Admission
        fields = ['student', 'cycle']  # Added cycle
        # Note: Other fields (school_class, section, etc.) might need dynamic queryset if required

# schools/forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Admission, SchoolClass, ClassSection, AdmissionCycle, SchoolProfile
import os
import logging

logger = logging.getLogger(__name__)

class StudentApplicationForm(forms.ModelForm):
    # Existing fields for cycle, class, section
    cycle = forms.ModelChoiceField(
        queryset=AdmissionCycle.objects.none(),
        empty_label="Select a Cycle",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'updateForm(this);'})
    )
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.none(),
        empty_label="Select a Class",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'updateForm(this);'})
    )
    section = forms.ModelChoiceField(
        queryset=ClassSection.objects.none(),
        empty_label="Select a Section",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Student Personal Information
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'})
    )
    middle_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter middle name (optional)'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'})
    )
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=Admission.GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nationality = forms.CharField(
        max_length=50,
        required=True,
        initial='Indian',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter nationality'})
    )
    aadhaar_number = forms.CharField(
        max_length=12,
        required=False,
        validators=[RegexValidator(r'^\d{12}$', 'Aadhaar must be 12 digits.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Aadhaar number (optional)'})
    )
    student_contact_number = forms.CharField(
        max_length=10,
        required=False,
        validators=[RegexValidator(r'^\d{10}$', 'Contact number must be 10 digits.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter student contact number (optional)'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'})
    )
    permanent_address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter permanent address'})
    )
    correspondence_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter correspondence address (optional)'})
    )
    caste = forms.ChoiceField(
        choices=Admission.CASTE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'caste_field'})
    )
    religion = forms.ChoiceField(
        choices=Admission.RELIGION_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    mother_tongue = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother tongue'})
    )
    blood_group = forms.ChoiceField(
        choices=Admission.BLOOD_GROUP_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Parent Information
    father_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter father’s name'})
    )
    father_occupation = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter father’s occupation'})
    )
    father_contact_number = forms.CharField(
        max_length=10,
        required=True,
        validators=[RegexValidator(r'^\d{10}$', 'Contact number must be 10 digits.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter father’s contact number'})
    )
    mother_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother’s name'})
    )
    mother_occupation = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother’s occupation'})
    )
    mother_contact_number = forms.CharField(
        max_length=10,
        required=True,
        validators=[RegexValidator(r'^\d{10}$', 'Contact number must be 10 digits.')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother’s contact number'})
    )

    # Academic Information
    previous_school_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter previous school name'})
    )
    previous_school_address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter previous school address'})
    )
    board_of_education = forms.ChoiceField(
        choices=Admission.BOARD_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    class_last_attended = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter class last attended (e.g., Class 10)'})
    )
    year_of_passing = forms.IntegerField(
        required=True,
        min_value=2000,
        max_value=2025,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter year of passing'})
    )
    percentage_obtained = forms.FloatField(
        required=True,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Enter percentage obtained'})
    )
    reason_for_leaving = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Reason for leaving previous school (optional)'})
    )

    # Documents
    birth_certificate = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg'})
    )
    aadhaar_card = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg'})
    )
    caste_certificate = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg', 'id': 'caste_certificate_field'})
    )
    previous_mark_sheet = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg'})
    )
    transfer_certificate = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg'})
    )
    passport_photo = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg'})
    )
    address_proof = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpg,.jpeg'})
    )

    class Meta:
        model = Admission
        fields = [
            'cycle', 'school_class', 'section',
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender',
            'nationality', 'aadhaar_number', 'student_contact_number', 'email',
            'permanent_address', 'correspondence_address', 'caste', 'religion',
            'mother_tongue', 'blood_group',
            'father_name', 'father_occupation', 'father_contact_number',
            'mother_name', 'mother_occupation', 'mother_contact_number',
            'previous_school_name', 'previous_school_address', 'board_of_education',
            'class_last_attended', 'year_of_passing', 'percentage_obtained', 'reason_for_leaving',
            'birth_certificate', 'aadhaar_card', 'caste_certificate',
            'previous_mark_sheet', 'transfer_certificate', 'passport_photo', 'address_proof',
        ]

    def __init__(self, *args, school_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Initializing StudentApplicationForm with school_id={school_id}, data={self.data}")
        if school_id:
            # Set cycle queryset
            self.fields['cycle'].queryset = AdmissionCycle.objects.filter(
                school_id=school_id, is_active=True
            ).order_by('-year')
            logger.debug(f"Cycle queryset: {[c.year for c in self.fields['cycle'].queryset]}")

            # Get cycle_id from form data or instance
            cycle_id = None
            if self.data.get('cycle'):
                try:
                    cycle_id = int(self.data.get('cycle'))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid cycle_id in form data: {self.data.get('cycle')}")
            elif self.instance and self.instance.cycle_id:
                cycle_id = self.instance.cycle_id
                logger.debug(f"Using instance cycle_id: {cycle_id}")

            # Set school_class queryset
            if cycle_id:
                self.fields['school_class'].queryset = SchoolClass.objects.filter(
                    school_id=school_id, cycle_id=cycle_id
                )
                logger.debug(f"School_class queryset for cycle_id={cycle_id}: {[c.grade for c in self.fields['school_class'].queryset]}")
            else:
                self.fields['school_class'].queryset = SchoolClass.objects.none()
                logger.debug("No cycle_id, setting school_class to none")

            # Get school_class_id from form data or instance
            class_id = None
            if self.data.get('school_class'):
                try:
                    class_id = int(self.data.get('school_class'))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid school_class_id in form data: {self.data.get('school_class')}")
            elif self.instance and self.instance.school_class_id:
                class_id = self.instance.school_class_id
                logger.debug(f"Using instance school_class_id: {class_id}")

            # Set section queryset
            if class_id and cycle_id:
                self.fields['section'].queryset = ClassSection.objects.filter(
                    school_class_id=class_id, cycle_id=cycle_id
                )
                logger.debug(f"Section queryset for class_id={class_id}, cycle_id={cycle_id}: {[s.section_name for s in self.fields['section'].queryset]}")
            elif self.instance and self.instance.section_id and self.instance.school_class_id and self.instance.cycle_id:
                self.fields['section'].queryset = ClassSection.objects.filter(
                    school_class_id=self.instance.school_class_id, cycle_id=self.instance.cycle_id
                )
                logger.debug(f"Section queryset from instance: {[s.section_name for s in self.fields['section'].queryset]}")
            else:
                self.fields['section'].queryset = ClassSection.objects.none()
                logger.debug("No class_id or cycle_id, setting section to none")

    def clean(self):
        cleaned_data = super().clean()
        caste = cleaned_data.get('caste')
        caste_certificate = cleaned_data.get('caste_certificate')

        # Require caste certificate for OBC, SC, ST, EWS
        if caste in ['OBC', 'SC', 'ST', 'EWS'] and not caste_certificate:
            self.add_error('caste_certificate', 'Caste certificate is required for this category.')

        # File upload validation (max 2MB, PDF/JPEG)
        for field_name in ['birth_certificate', 'aadhaar_card', 'caste_certificate', 'previous_mark_sheet', 'transfer_certificate', 'passport_photo', 'address_proof']:
            file = cleaned_data.get(field_name)
            if file:
                if file.size > 2 * 1024 * 1024:  # 2MB
                    self.add_error(field_name, 'File size must not exceed 2MB.')
                ext = os.path.splitext(file.name)[1].lower()
                allowed_exts = ['.pdf', '.jpg', '.jpeg']
                if field_name == 'passport_photo':
                    allowed_exts = ['.jpg', '.jpeg']
                if ext not in allowed_exts:
                    self.add_error(field_name, f'File must be {", ".join(allowed_exts)}.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

from .models import SchoolProfile, SchoolRating
class SchoolRatingForm(forms.ModelForm):
    class Meta:
        model = SchoolRating
        fields = ['rating']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',  # Allow increments of 0.1 (e.g., 4.3, 4.4)
                'min': '1.0',
                'max': '5.0'
            }),
        }

from django import forms
from .models import SchoolGallery

class SchoolGalleryForm(forms.ModelForm):
    class Meta:
        model = SchoolGallery
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a caption (optional)'}),
        }


from django import forms
from .models import SchoolTestimonial

class SchoolTestimonialForm(forms.ModelForm):
    class Meta:
        model = SchoolTestimonial
        fields = ['author_name', 'author_role', 'message']
        widgets = {
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the author\'s name'}),
            'author_role': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter the testimonial message'}),
        }



# schools/forms.py
from django import forms
from .models import SchoolProfile, SchoolClass, ClassSection, AdmissionCycle

class AdmissionCycleForm(forms.ModelForm):
    class Meta:
        model = AdmissionCycle
        fields = ['year', 'start_date', 'end_date', 'is_active', 'is_archived']
        widgets = {
            'year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2025-2026'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_archived': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)  # Pass school from view
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['year'].widget.attrs['readonly'] = True  # Prevent editing year after creation
        if self.school:
            self.fields['school'] = forms.ModelChoiceField(
                queryset=SchoolProfile.objects.filter(id=self.school.id),
                widget=forms.HiddenInput(),
                initial=self.school,
                required=False
            )

    def clean_year(self):
        year = self.cleaned_data['year']
        if self.school and AdmissionCycle.objects.filter(school=self.school, year=year).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A cycle with this year already exists for your school.")
        return year

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.school and not instance.school_id:  # Only set if not already set
            instance.school = self.school
        if commit:
            instance.save()
        return instance