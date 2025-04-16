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
from .models import Application, AdmissionCycle, Degree

class ApplicationForm(forms.ModelForm):
    # Application Information (Category 1)
    entrance_exam = forms.CharField(max_length=100, required=False, label="Entrance Exam")
    entrance_score = forms.CharField(max_length=50, required=False, label="Entrance Score/Rank")

    # Personal Information (Category 2)
    first_name = forms.CharField(max_length=50, required=True, label="First Name")
    middle_name = forms.CharField(max_length=50, required=False, label="Middle Name")
    last_name = forms.CharField(max_length=50, required=True, label="Last Name")
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True, label="Date of Birth")
    gender = forms.ChoiceField(choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')), required=True, label="Gender")
    nationality = forms.CharField(max_length=50, initial="Indian", required=True, label="Nationality")
    aadhaar_number = forms.CharField(max_length=12, required=False, label="Aadhaar Number")
    contact_number = forms.CharField(max_length=15, required=True, label="Contact Number")
    email = forms.EmailField(required=True, label="Email")
    permanent_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, label="Permanent Address")
    correspondence_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Correspondence Address")
    caste = forms.CharField(max_length=50, required=False, label="Caste/Category")
    religion = forms.CharField(max_length=50, required=False, label="Religion")
    mother_tongue = forms.CharField(max_length=50, required=False, label="Mother Tongue")

    # Parent Information (Category 3)
    father_name = forms.CharField(max_length=100, required=True, label="Father’s Name")
    father_occupation = forms.CharField(max_length=100, required=False, label="Father’s Occupation")
    father_contact = forms.CharField(max_length=15, required=False, label="Father’s Contact Number")
    mother_name = forms.CharField(max_length=100, required=True, label="Mother’s Name")
    mother_occupation = forms.CharField(max_length=100, required=False, label="Mother’s Occupation")
    mother_contact = forms.CharField(max_length=15, required=False, label="Mother’s Contact Number")
    family_income = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label="Annual Family Income")

    # Academic Information (Category 4)
    class_12_school = forms.CharField(max_length=200, required=True, label="Class 12 School Name")
    class_12_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=True, label="Class 12 School Address")
    class_12_board = forms.ChoiceField(choices=(('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('State', 'State Board'), ('IB', 'IB'), ('Other', 'Other')), required=True, label="Class 12 Board")
    class_12_year = forms.CharField(max_length=4, required=True, label="Class 12 Year of Passing")
    class_12_percentage = forms.CharField(max_length=10, required=True, label="Class 12 Percentage/CGPA")
    class_12_stream = forms.CharField(max_length=200, required=True, label="Class 12 Stream")
    class_10_school = forms.CharField(max_length=200, required=True, label="Class 10 School Name")
    class_10_board = forms.ChoiceField(choices=(('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('State', 'State Board'), ('IB', 'IB'), ('Other', 'Other')), required=True, label="Class 10 Board")
    class_10_year = forms.CharField(max_length=4, required=True, label="Class 10 Year of Passing")
    class_10_percentage = forms.CharField(max_length=10, required=True, label="Class 10 Percentage/CGPA")
    other_qualifications = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Other Qualifications")
    achievements = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Achievements")

    # Documents (Category 5)
    birth_certificate = forms.FileField(required=True, label="Birth Certificate")
    aadhaar_card = forms.FileField(required=False, label="Aadhaar Card")
    caste_certificate = forms.FileField(required=False, label="Caste Certificate")
    class_12_mark_sheet = forms.FileField(required=True, label="Class 12 Mark Sheet")
    class_10_mark_sheet = forms.FileField(required=True, label="Class 10 Mark Sheet")
    transfer_certificate = forms.FileField(required=True, label="Transfer Certificate")
    passport_photo = forms.FileField(required=True, label="Passport Photo")
    address_proof = forms.FileField(required=True, label="Address Proof")
    entrance_scorecard = forms.FileField(required=False, label="Entrance Exam Scorecard")
    recommendation_letter = forms.FileField(required=False, label="Recommendation Letter")

    # Existing cycle field
    cycle = forms.ModelChoiceField(
        queryset=AdmissionCycle.objects.none(),
        required=True,
        widget=forms.HiddenInput(),
        label="Admission Cycle"
    )

    # Updated degree field
    degree = forms.ModelChoiceField(
        queryset=Degree.objects.none(),
        required=False,  # Changed to optional
        label="Degree"
    )

    class Meta:
        model = Application
        fields = [
            'degree', 'entrance_exam', 'entrance_score',
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'nationality',
            'aadhaar_number', 'contact_number', 'email', 'permanent_address', 'correspondence_address',
            'caste', 'religion', 'mother_tongue',
            'father_name', 'father_occupation', 'father_contact',
            'mother_name', 'mother_occupation', 'mother_contact', 'family_income',
            'class_12_school', 'class_12_address', 'class_12_board', 'class_12_year',
            'class_12_percentage', 'class_12_stream',
            'class_10_school', 'class_10_board', 'class_10_year', 'class_10_percentage',
            'other_qualifications', 'achievements',
            'birth_certificate', 'aadhaar_card', 'caste_certificate',
            'class_12_mark_sheet', 'class_10_mark_sheet', 'transfer_certificate',
            'passport_photo', 'address_proof', 'entrance_scorecard', 'recommendation_letter',
            'cycle'
        ]

    def __init__(self, college, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        # Apply form-control to text fields
        for field in self.fields:
            if field not in ['birth_certificate', 'aadhaar_card', 'caste_certificate',
                            'class_12_mark_sheet', 'class_10_mark_sheet', 'transfer_certificate',
                            'passport_photo', 'address_proof', 'entrance_scorecard', 'recommendation_letter',
                            'date_of_birth', 'gender', 'class_12_board', 'class_12_stream',
                            'class_10_board', 'cycle', 'degree']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            elif field in ['date_of_birth', 'gender', 'class_12_board', 'class_12_stream', 'class_10_board', 'degree']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control-file'})
        # Cycle logic (unchanged)
        self.fields['cycle'].queryset = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).order_by('year')
        if 'initial' in kwargs and 'cycle_id' in kwargs['initial']:
            selected_cycle = AdmissionCycle.objects.filter(id=kwargs['initial']['cycle_id'], college=college).first()
            if selected_cycle:
                self.fields['cycle'].initial = selected_cycle
                self.initial['cycle'] = selected_cycle
        elif college:
            active_cycle = AdmissionCycle.objects.filter(college=college, is_active=True, is_archived=False).first()
            if active_cycle:
                self.fields['cycle'].initial = active_cycle
                self.initial['cycle'] = active_cycle
        # Degree logic
        if college:
            self.fields['degree'].queryset = Degree.objects.filter(college=college, cycle__is_active=True, cycle__is_archived=False).order_by('name')
            if 'initial' in kwargs and 'degree_id' in kwargs['initial']:
                selected_degree = Degree.objects.filter(id=kwargs['initial']['degree_id'], college=college).first()
                if selected_degree:
                    self.fields['degree'].initial = selected_degree
                    self.initial['degree'] = selected_degree

    def clean(self):
        cleaned_data = super().clean()
        # Cycle validation
        selected_cycle = cleaned_data.get('cycle')
        if not selected_cycle:
            raise forms.ValidationError("Admission cycle is required.")
        # Removed degree validation to make it optional
        # Aadhaar validation
        aadhaar = cleaned_data.get('aadhaar_number')
        if aadhaar and (not aadhaar.isdigit() or len(aadhaar) != 12):
            self.add_error('aadhaar_number', "Aadhaar number must be 12 digits.")
        # Percentage validation
        class_12_percentage = cleaned_data.get('class_12_percentage')
        if class_12_percentage:
            try:
                float(class_12_percentage.replace('%', ''))
            except ValueError:
                self.add_error('class_12_percentage', "Enter a valid percentage (e.g., '92%' or '9.2').")
        class_10_percentage = cleaned_data.get('class_10_percentage')
        if class_10_percentage:
            try:
                float(class_10_percentage.replace('%', ''))
            except ValueError:
                self.add_error('class_10_percentage', "Enter a valid percentage (e.g., '95%' or '9.5').")
        # Year validation
        class_12_year = cleaned_data.get('class_12_year')
        if class_12_year and (not class_12_year.isdigit() or len(class_12_year) != 4):
            self.add_error('class_12_year', "Enter a valid 4-digit year (e.g., '2023').")
        class_10_year = cleaned_data.get('class_10_year')
        if class_10_year and (not class_10_year.isdigit() or len(class_10_year) != 4):
            self.add_error('class_10_year', "Enter a valid 4-digit year (e.g., '2021').")
        # File type validation
        for field in ['birth_certificate', 'class_12_mark_sheet', 'class_10_mark_sheet', 'transfer_certificate', 'address_proof']:
            file = cleaned_data.get(field)
            if file and not file.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                self.add_error(field, "File must be a PDF or image (JPG, JPEG, PNG).")
        for field in ['aadhaar_card', 'caste_certificate', 'entrance_scorecard', 'recommendation_letter']:
            file = cleaned_data.get(field)
            if file and not file.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                self.add_error(field, "File must be a PDF or image (JPG, JPEG, PNG).")
        if cleaned_data.get('passport_photo') and not cleaned_data['passport_photo'].name.lower().endswith(('.jpg', '.jpeg', '.png')):
            self.add_error('passport_photo', "Passport photo must be an image (JPG, JPEG, PNG).")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.cycle = self.cleaned_data['cycle']
        instance.degree = self.cleaned_data.get('degree')  # Use .get() to handle optional
        if commit:
            instance.save()
        return instance