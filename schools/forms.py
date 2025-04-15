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

from django import forms
from .models import SchoolClass, ClassSection, Admission, AdmissionCycle

class StudentApplicationForm(forms.ModelForm):
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
    parent_name = forms.CharField(
        max_length=255,
        required=True,
        label="Parent's Name",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    contact_number = forms.CharField(
        max_length=15,
        required=True,
        label="Contact Number",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Admission
        fields = ['parent_name', 'contact_number', 'email']

    def __init__(self, *args, school_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school_id:
            self.fields['cycle'].queryset = AdmissionCycle.objects.filter(school_id=school_id, is_active=True).order_by('-year')
            cycle_id = self.data.get('cycle') if 'cycle' in self.data else (self.instance.cycle_id if self.instance.cycle_id else None)
            if cycle_id:
                self.fields['school_class'].queryset = SchoolClass.objects.filter(school_id=school_id, cycle_id=cycle_id)
                class_id = self.data.get('school_class') if 'school_class' in self.data else (self.instance.school_class_id if self.instance.school_class_id else None)
                if class_id:
                    self.fields['section'].queryset = ClassSection.objects.filter(school_class_id=class_id, cycle_id=cycle_id)
                elif self.instance.section_id and self.instance.school_class_id:
                    self.fields['section'].queryset = ClassSection.objects.filter(school_class_id=self.instance.school_class_id, cycle_id=cycle_id)

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
            'year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2025'}),
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