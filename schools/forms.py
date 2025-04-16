from django import forms
from .models import SchoolProfile

class SchoolProfileForm(forms.ModelForm):
    class Meta:
        model = SchoolProfile
        # Exclude fields that are managed automatically
        exclude = ['user', 'created_at', 'updated_at']
        # Customize widgets for better user experience
        widgets = {
            'street_address': forms.TextInput(attrs={'placeholder': 'e.g., 123 Main Street'}),
            'landmark': forms.TextInput(attrs={'placeholder': 'e.g., Near XYZ Park'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g., Hyderabad'}),
            'district': forms.TextInput(attrs={'placeholder': 'e.g., Ranga Reddy'}),
            'state': forms.TextInput(attrs={'placeholder': 'e.g., Telangana'}),
            'pincode': forms.TextInput(attrs={'placeholder': 'e.g., 500081'}),
            'country': forms.TextInput(attrs={'placeholder': 'e.g., India'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'e.g., admin@school.com'}),
            'contact_phone': forms.TextInput(attrs={'placeholder': 'e.g., +91 9876543210'}),
            'principal_name': forms.TextInput(attrs={'placeholder': 'e.g., Dr. John Doe'}),
            'accreditation': forms.TextInput(attrs={'placeholder': 'e.g., CBSE, ICSE'}),
            'established_year': forms.NumberInput(attrs={'placeholder': 'e.g., 1995'}),
            'website': forms.URLInput(attrs={'placeholder': 'e.g., https://school.com'}),
            'total_students': forms.NumberInput(attrs={'placeholder': 'e.g., 1200'}),
            'total_teachers': forms.NumberInput(attrs={'placeholder': 'e.g., 50'}),
            'profile_pic': forms.FileInput(),
            'school_type': forms.Select(),
            'medium_of_instruction': forms.TextInput(attrs={'placeholder': 'e.g., English'}),
            'start_grade': forms.Select(choices=[(i, f"Grade {i}") for i in range(1, 13)]),
            'end_grade': forms.Select(choices=[(i, f"Grade {i}") for i in range(1, 13)]),
            'facilities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e.g., Library, Science Labs, Sports Ground'}),
            'school_motto': forms.TextInput(attrs={'placeholder': 'e.g., Education for All'}),
            'affiliation_number': forms.TextInput(attrs={'placeholder': 'e.g., CBSE-12345'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_grade = cleaned_data.get('start_grade')
        end_grade = cleaned_data.get('end_grade')

        # Validation: Ensure start_grade <= end_grade
        if start_grade and end_grade and start_grade > end_grade:
            raise forms.ValidationError("Start grade must be less than or equal to end grade.")
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