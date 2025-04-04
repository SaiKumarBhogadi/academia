# colleges/forms.py
from django import forms
from .models import CollegeProfile, Department, Degree, Course

class CollegeProfileForm(forms.ModelForm):
    class Meta:
        model = CollegeProfile
        fields = [
            'college_name', 'principal_name', 'established_year', 'street_address', 'city',
            'state', 'pincode', 'country', 'contact_email', 'contact_phone', 'website',
            'college_type', 'affiliation', 'accreditation', 'hostel_availability',
            'hostel_capacity_boys', 'hostel_capacity_girls', 'library', 'library_books_count',
            'labs', 'placement_cell', 'placement_percentage', 'top_recruiters',
            'other_facilities', 'profile_pic'
        ]
        widgets = {
            'college_name': forms.TextInput(attrs={'class': 'form-control'}),
            'principal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'street_address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'college_type': forms.Select(attrs={'class': 'form-control'}),
            'affiliation': forms.TextInput(attrs={'class': 'form-control'}),
            'accreditation': forms.TextInput(attrs={'class': 'form-control'}),
            'hostel_availability': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'hostel_capacity_boys': forms.NumberInput(attrs={'class': 'form-control'}),
            'hostel_capacity_girls': forms.NumberInput(attrs={'class': 'form-control'}),
            'library': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'library_books_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'labs': forms.Textarea(attrs={'class': 'form-control'}),
            'placement_cell': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'placement_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'top_recruiters': forms.Textarea(attrs={'class': 'form-control'}),
            'other_facilities': forms.Textarea(attrs={'class': 'form-control'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }

class DegreeForm(forms.ModelForm):
    class Meta:
        model = Degree
        fields = ['name', 'duration', 'eligibility_criteria']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'eligibility_criteria': forms.Textarea(attrs={'class': 'form-control'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'hod_name', 'faculty_count', 'labs', 'total_seats', 'fees_per_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'hod_name': forms.TextInput(attrs={'class': 'form-control'}),
            'faculty_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'labs': forms.Textarea(attrs={'class': 'form-control'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'fees_per_year': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'name', 'semester', 'credits']
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control'}),
        }