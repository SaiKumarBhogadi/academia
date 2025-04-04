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
from .models import SchoolClass, ClassSection

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['grade', 'total_sections']
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Grade 1'}),
            'total_sections': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class ClassSectionForm(forms.ModelForm):
    class Meta:
        model = ClassSection
        fields = ['section_name', 'total_seats']
        widgets = {
            'section_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Section A'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


from django import forms
from core.models import User  # Import User from core.models
from .models import SchoolClass, ClassSection, Admission
class AdmissionForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=User.objects.filter(user_type='student'), widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Admission
        fields = ['student']

class StudentApplicationForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['parent_name', 'contact_number', 'email']
        widgets = {
            'parent_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter parent name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter contact number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email address'}),
        }


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