from django.db import models
from core.models import User
from django.utils import timezone

class CollegeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='college_profile')
    college_name = models.CharField(max_length=255)
    principal_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    alternate_phone_number = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField()
    college_type = models.CharField(
        max_length=50,
        choices=[('Private', 'Private'), ('Government', 'Government'), ('Autonomous', 'Autonomous')]
    )
    affiliation = models.CharField(max_length=100)
    accreditation = models.CharField(
        max_length=100,
        choices=[('AICTE', 'AICTE'), ('NAAC', 'NAAC'), ('NBA', 'NBA'), ('', 'Other')]
    )
    courses_offered = models.TextField(blank=True, null=True)
    streams_available = models.TextField(blank=True, null=True)
    medium_of_instruction = models.CharField(
        max_length=50,
        choices=[('English', 'English'), ('Telugu', 'Telugu'), ('Hindi', 'Hindi'), ('Other', 'Other')],
        blank=True,
        null=True
    )
    established_year = models.IntegerField()
    total_students = models.IntegerField()
    total_faculty = models.IntegerField()
    college_code = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    hostel_availability = models.BooleanField(default=False)
    hostel_capacity_boys = models.IntegerField(blank=True, null=True)
    hostel_capacity_girls = models.IntegerField(blank=True, null=True)
    library = models.BooleanField(default=False)
    library_books_count = models.IntegerField(blank=True, null=True)
    labs = models.TextField(blank=True, null=True)
    placement_cell = models.BooleanField(default=False)
    placement_percentage = models.FloatField(blank=True, null=True)
    top_recruiters = models.TextField(blank=True, null=True)
    other_facilities = models.TextField(blank=True, null=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10)
    profile_pic = models.ImageField(upload_to='college_logos/', blank=True, null=True)
    accreditation_certificate = models.FileField(upload_to='college_certificates/', blank=True, null=True)
    brochure = models.FileField(upload_to='college_brochures/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.college_name

from django.db import models

class AdmissionCycle(models.Model):
    college = models.ForeignKey(CollegeProfile, on_delete=models.CASCADE)
    year = models.CharField(max_length=9)  # Remove unique=True
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('college', 'year')  # Ensure year is unique per college

    def __str__(self):
        return f"{self.year} ({self.start_date} - {self.end_date}) for {self.college.college_name}"


class Degree(models.Model):
    college = models.ForeignKey(CollegeProfile, on_delete=models.CASCADE, related_name='degrees')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, help_text="The cycle this degree is offered in")
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    eligibility_criteria = models.TextField(blank=True)

    class Meta:
        unique_together = ('college', 'cycle', 'name')  # Unique degree name per college and cycle

    def __str__(self):
        return f"{self.name} - {self.cycle.year}"

class Department(models.Model):
    college = models.ForeignKey(CollegeProfile, on_delete=models.CASCADE, related_name='departments')
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='departments')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, help_text="The cycle this department is offered in")
    name = models.CharField(max_length=100)
    hod_name = models.CharField(max_length=100, blank=True)
    faculty_count = models.PositiveIntegerField(default=0)
    labs = models.TextField(blank=True)
    fees_per_year = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('degree', 'cycle', 'name')  # Unique department name per degree and cycle

    @property
    def total_seats(self):
        return sum(section.total_seats for section in self.sections.all())
    
    def admissions_left(self):
        # Get all sections for this department
        sections = self.sections.all()
        # Count total filled seats across all sections
        filled_seats = sum(section.seats.filter(is_filled=True).count() for section in sections)
        # Calculate remaining seats
        return max(0, self.total_seats - filled_seats)


    def __str__(self):
        return f"{self.name} - {self.degree.name} ({self.cycle.year})"

class Section(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='sections')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, help_text="The cycle this section is offered in")
    section_name = models.CharField(max_length=50)
    total_seats = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('department', 'section_name', 'cycle')  # Unique section per department and cycle

    def __str__(self):
        return f"{self.section_name} - {self.department.name} - {self.cycle.year}"

class Course(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='courses')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, help_text="The cycle this course is offered in")
    course_code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    credits = models.PositiveIntegerField()

    class Meta:
        unique_together = ('department', 'course_code', 'name')  # Unique course code and name per department

    def __str__(self):
        return f"{self.course_code} - {self.name} ({self.cycle.year})"

class Seat(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10, blank=True)
    is_filled = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.seat_number:
            existing_seats = Seat.objects.filter(section=self.section).count()
            self.seat_number = f"{self.section.section_name} {existing_seats + 1}"  # e.g., "A3 1"
        super().save(*args, **kwargs)

class Application(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn'),
    )

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    degree = models.ForeignKey('Degree', on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='applications')
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    apply_date = models.DateTimeField(auto_now_add=True)
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, related_name='applications')

    # Application Information (Category 1)
    admission_id = models.CharField(max_length=20, unique=True, blank=True)  # e.g., "COL-2025-001"
    entrance_exam = models.CharField(max_length=100, blank=True)  # e.g., "JEE Main"
    entrance_score = models.CharField(max_length=50, blank=True)  # e.g., "Rank: 1500"

    # Personal Information (Category 2)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=(('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')))
    nationality = models.CharField(max_length=50, default="Indian")
    aadhaar_number = models.CharField(max_length=12, blank=True)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    permanent_address = models.TextField()
    correspondence_address = models.TextField(blank=True)
    caste = models.CharField(max_length=50, blank=True)  # e.g., "General", "OBC"
    religion = models.CharField(max_length=50, blank=True)
    mother_tongue = models.CharField(max_length=50, blank=True)

    # Parent Information (Category 3)
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100, blank=True)
    father_contact = models.CharField(max_length=15, blank=True)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100, blank=True)
    mother_contact = models.CharField(max_length=15, blank=True)
    family_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Academic Information (Category 4)
    class_12_school = models.CharField(max_length=200)
    class_12_address = models.TextField()
    class_12_board = models.CharField(max_length=50, choices=(('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('State', 'State Board'), ('IB', 'IB'), ('Other', 'Other')))
    class_12_year = models.CharField(max_length=4)
    class_12_percentage = models.CharField(max_length=10)  # e.g., "92%"
    class_12_stream = models.CharField(max_length=50)
    class_10_school = models.CharField(max_length=200)
    class_10_board = models.CharField(max_length=50, choices=(('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('State', 'State Board'), ('IB', 'IB'), ('Other', 'Other')))
    class_10_year = models.CharField(max_length=4)
    class_10_percentage = models.CharField(max_length=10)  # e.g., "95%"
    other_qualifications = models.TextField(blank=True)
    achievements = models.TextField(blank=True)

    # Documents (Category 5)
    birth_certificate = models.FileField(upload_to='applications/documents/%Y/%m/%d/')
    aadhaar_card = models.FileField(upload_to='applications/documents/%Y/%m/%d/', blank=True)
    caste_certificate = models.FileField(upload_to='applications/documents/%Y/%m/%d/', blank=True)
    class_12_mark_sheet = models.FileField(upload_to='applications/documents/%Y/%m/%d/')
    class_10_mark_sheet = models.FileField(upload_to='applications/documents/%Y/%m/%d/')
    transfer_certificate = models.FileField(upload_to='applications/documents/%Y/%m/%d/')
    passport_photo = models.FileField(upload_to='applications/documents/%Y/%m/%d/')
    address_proof = models.FileField(upload_to='applications/documents/%Y/%m/%d/')
    entrance_scorecard = models.FileField(upload_to='applications/documents/%Y/%m/%d/', blank=True)
    recommendation_letter = models.FileField(upload_to='applications/documents/%Y/%m/%d/', blank=True)

    class Meta:
        verbose_name = "College Application"
        verbose_name_plural = "College Applications"

    def save(self, *args, **kwargs):
        if not self.admission_id:
            year = self.cycle.year.split('-')[0]
            count = Application.objects.filter(cycle=self.cycle).count() + 1
            self.admission_id = f"COL-{year}-{count:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.admission_id} - {self.student.username} - {self.department.name}"