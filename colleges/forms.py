from django import forms
from .models import CollegeProfile, Department, Degree, Course, Section, AdmissionCycle
from .models import Application
from django.utils import timezone

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

# colleges/forms.py
from django import forms
from .models import AdmissionCycle, Degree, Department, Section, Course, CollegeProfile

from django import forms
from .models import AdmissionCycle

from django import forms
from .models import AdmissionCycle

class AdmissionCycleForm(forms.ModelForm):
    class Meta:
        model = AdmissionCycle
        fields = ['year', 'start_date', 'end_date', 'is_active', 'is_archived']

    def __init__(self, college, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        self.fields['year'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_archived'].widget.attrs.update({'class': 'form-check-input'})
        self.college = college  # Store college instance for validation

    def clean_year(self):
        year = self.cleaned_data['year']
        # Check for existing cycles, excluding the current instance if editing
        queryset = AdmissionCycle.objects.filter(college=self.college, year=year)
        if self.instance and self.instance.pk:  # If editing
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError(
                "This year already has a cycle for this college. Please choose a different year or edit the existing one."
            )
        return year

    
class DegreeForm(forms.ModelForm):
    class Meta:
        model = Degree
        fields = ['name', 'duration', 'eligibility_criteria']
        widgets = {
            'eligibility_criteria': forms.Textarea(attrs={'rows': 3}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'hod_name', 'faculty_count', 'labs', 'fees_per_year']
        widgets = {
            'labs': forms.Textarea(attrs={'rows': 3}),
        }

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['section_name', 'total_seats']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_code', 'name', 'semester', 'credits']


from django import forms
from django.utils import timezone
from .models import Application, AdmissionCycle

from django import forms
from django.utils import timezone
from .models import Application, AdmissionCycle

class ApplicationForm(forms.ModelForm):
    parent_name = forms.CharField(max_length=100, required=True)
    contact_number = forms.CharField(max_length=15, required=True)
    email = forms.EmailField(required=True)
    cycle = forms.ModelChoiceField(
        queryset=AdmissionCycle.objects.none(),
        required=True,
        widget=forms.HiddenInput(),  # Change to hidden input
        label="Admission Cycle"  # Label is optional since it's hidden
    )

    class Meta:
        model = Application
        fields = ['parent_name', 'contact_number', 'email', 'cycle']

    def __init__(self, college, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['parent_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['contact_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['cycle'].queryset = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).order_by('year')
        if 'initial' in kwargs and 'cycle_id' in kwargs['initial']:
            selected_cycle = AdmissionCycle.objects.filter(id=kwargs['initial']['cycle_id'], college=college).first()
            if selected_cycle:
                self.fields['cycle'].initial = selected_cycle
                self.initial['cycle'] = selected_cycle  # Force initial value
        elif college:
            active_cycle = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).first()
            if active_cycle:
                self.fields['cycle'].initial = active_cycle
                self.initial['cycle'] = active_cycle

    def clean(self):
        cleaned_data = super().clean()
        selected_cycle = cleaned_data.get('cycle')
        if not selected_cycle:
            raise forms.ValidationError("Admission cycle is required but not set.")
        # Temporarily disable date validation for testing
        # if timezone.now().date() < selected_cycle.start_date or timezone.now().date() > selected_cycle.end_date:
        #     raise forms.ValidationError(f"Applications are not accepted outside the cycle period ({selected_cycle.start_date} to {selected_cycle.end_date}).")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.cycle = self.cleaned_data['cycle']  # Use the hidden cycle value
        if commit:
            instance.save()
        return instance