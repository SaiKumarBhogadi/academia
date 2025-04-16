from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CollegeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='college_profile')
    college_name = models.CharField(max_length=255)
    principal_name = models.CharField(max_length=100, blank=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, default="India")
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    website = models.URLField(blank=True)
    COLLEGE_TYPE_CHOICES = (
        ('government', 'Government'),
        ('private', 'Private'),
        ('autonomous', 'Autonomous'),
    )
    college_type = models.CharField(max_length=20, choices=COLLEGE_TYPE_CHOICES, default='private')
    affiliation = models.CharField(max_length=255, blank=True)
    accreditation = models.CharField(max_length=100, blank=True)
    hostel_availability = models.BooleanField(default=False)
    hostel_capacity_boys = models.PositiveIntegerField(blank=True, null=True)
    hostel_capacity_girls = models.PositiveIntegerField(blank=True, null=True)
    library = models.BooleanField(default=False)
    library_books_count = models.PositiveIntegerField(blank=True, null=True)
    labs = models.TextField(blank=True)
    placement_cell = models.BooleanField(default=False)
    placement_percentage = models.FloatField(blank=True, null=True)
    top_recruiters = models.TextField(blank=True)
    other_facilities = models.TextField(blank=True)
    profile_pic = models.ImageField(upload_to='college_profiles/', blank=True, null=True)

    def __str__(self):
        return self.college_name

    class Meta:
        verbose_name = "College Profile"
        verbose_name_plural = "College Profiles"

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