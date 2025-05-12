from django.db import models
from core.models import User

class SchoolProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_profile')
    school_name = models.CharField(max_length=255)
    principal_name = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=15)
    alternate_phone_number = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField()
    school_type = models.CharField(
        max_length=50,
        choices=[('Private', 'Private'), ('Public', 'Public'), ('Government Aided', 'Government Aided')]
    )
    board_affiliation = models.CharField(
        max_length=50,
        choices=[('CBSE', 'CBSE'), ('ICSE', 'ICSE'), ('State Board', 'State Board'), ('IB', 'IB'), ('Other', 'Other')]
    )
    medium_of_instruction = models.CharField(
        max_length=50,
        choices=[('English', 'English'), ('Telugu', 'Telugu'), ('Hindi', 'Hindi'), ('Other', 'Other')]
    )
    established_year = models.IntegerField()
    total_students = models.IntegerField()
    total_teachers = models.IntegerField()
    school_code = models.CharField(max_length=50, blank=True, null=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    affiliation_certificate = models.FileField(upload_to='school_certificates/', blank=True, null=True)
    brochure = models.FileField(upload_to='school_brochures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.school_name

# Admission Cycle Model (Added)
# schools/models.py
from django.db import models

class AdmissionCycle(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='cycles')
    year = models.CharField(max_length=9)  # Removed unique=True, relying on unique_together
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school', 'year')  # Prevent duplicate cycles for the same school

    def __str__(self):
        return f"{self.year} Cycle - {self.school.school_name}"
    

    
# SchoolClass Model (Added cycle)
class SchoolClass(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='classes')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, related_name='classes', null=True, blank=True)  # Nullable for now
    grade = models.CharField(max_length=50)
    total_sections = models.PositiveIntegerField(default=1)

    def __str__(self):
        cycle_info = f"(Cycle: {self.cycle.year})" if self.cycle else "(No Cycle)"
        return f"{self.grade} - {self.school.school_name} {cycle_info}".strip()

# ClassSection Model (Added cycle, removed filled_seats for dynamic calculation)
class ClassSection(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, related_name='sections', null=True, blank=True)  # Nullable for now
    section_name = models.CharField(max_length=10)
    total_seats = models.PositiveIntegerField(default=40)

    def available_seats(self):
        return self.total_seats - self.seats.filter(is_filled=True).count()

    def __str__(self):
        cycle_info = f"(Cycle: {self.cycle.year})" if self.cycle else "(No Cycle)"
        return f"{self.school_class.grade if self.school_class else 'Unknown Class'} - {self.section_name} {cycle_info}".strip()

# Seat Model (Unchanged)
class Seat(models.Model):
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_filled = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='seats')
    seat_order = models.PositiveIntegerField(blank=True, null=True, help_text="Numeric part of seat_number for ordering")

    def save(self, *args, **kwargs):
        if not self.seat_order and self.seat_number:
            # Extract numeric part (e.g., "A1" -> 1)
            self.seat_order = int(''.join(filter(str.isdigit, self.seat_number)))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.section} - Seat {self.seat_number}"

# Admission Model (Added cycle)
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
# from core.models import User, SchoolProfile, AdmissionCycle, SchoolClass, ClassSection, Seat

class Admission(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    CASTE_CHOICES = [
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('EWS', 'EWS'),
        ('Other', 'Other'),
    ]
    RELIGION_CHOICES = [
        ('Hindu', 'Hindu'),
        ('Muslim', 'Muslim'),
        ('Christian', 'Christian'),
        ('Sikh', 'Sikh'),
        ('Other', 'Other'),
    ]
    BOARD_CHOICES = [
        ('CBSE', 'CBSE'),
        ('ICSE', 'ICSE'),
        ('State Board', 'State Board'),
        ('Other', 'Other'),
    ]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    # Existing fields (unchanged)
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='admissions')
    cycle = models.ForeignKey(AdmissionCycle, on_delete=models.CASCADE, related_name='admissions', null=True, blank=True)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='admissions')
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='admissions')
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name='admission', null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admissions', null=True)
    email = models.EmailField()  # Kept, made mandatory
    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admission_id = models.CharField(max_length=20, unique=True, blank=True)

    # New fields: Student Personal Information
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=50, default='Indian')
    aadhaar_number = models.CharField(
        max_length=12, 
        blank=True, 
        validators=[RegexValidator(r'^\d{12}$', 'Aadhaar must be 12 digits.')]
    )
    student_contact_number = models.CharField(
        max_length=10, 
        blank=True, 
        validators=[RegexValidator(r'^\d{10}$', 'Contact number must be 10 digits.')]
    )
    permanent_address = models.TextField()
    correspondence_address = models.TextField(blank=True)
    caste = models.CharField(max_length=20, choices=CASTE_CHOICES)
    religion = models.CharField(max_length=20, choices=RELIGION_CHOICES)
    mother_tongue = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)

    # New fields: Parent Information
    father_name = models.CharField(max_length=255)
    father_occupation = models.CharField(max_length=100)
    father_contact_number = models.CharField(
        max_length=10, 
        validators=[RegexValidator(r'^\d{10}$', 'Contact number must be 10 digits.')]
    )
    mother_name = models.CharField(max_length=255)
    mother_occupation = models.CharField(max_length=100)
    mother_contact_number = models.CharField(
        max_length=10, 
        validators=[RegexValidator(r'^\d{10}$', 'Contact number must be 10 digits.')]
    )

    # New fields: Academic Information
    previous_school_name = models.CharField(max_length=200)
    previous_school_address = models.TextField()
    board_of_education = models.CharField(max_length=20, choices=BOARD_CHOICES)
    class_last_attended = models.CharField(max_length=20)
    year_of_passing = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2025)]
    )
    percentage_obtained = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    reason_for_leaving = models.TextField(blank=True)

    # New fields: Documents
    birth_certificate = models.FileField(upload_to='documents/%Y/%m/%d/')
    aadhaar_card = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True)
    caste_certificate = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True)
    previous_mark_sheet = models.FileField(upload_to='documents/%Y/%m/%d/')
    transfer_certificate = models.FileField(upload_to='documents/%Y/%m/%d/')
    passport_photo = models.FileField(upload_to='documents/%Y/%m/%d/')
    address_proof = models.FileField(upload_to='documents/%Y/%m/%d/')

    

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        if not self.admission_id:
            year = self.admission_date.year
            last_admission = Admission.objects.filter(
                admission_id__startswith=f"ADM-{year}-"
            ).order_by('-admission_id').first()
            if last_admission:
                last_number = int(last_admission.admission_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.admission_id = f"ADM-{year}-{new_number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.section.section_name if self.section else 'No Section'}"

    class Meta:
        verbose_name = "Admission"
        verbose_name_plural = "Admissions"




from django.core.validators import MinValueValidator, MaxValueValidator  # Moved here for consistency
class SchoolRating(models.Model):
    school_profile = models.OneToOneField(SchoolProfile, on_delete=models.CASCADE, related_name='rating')
    rating = models.FloatField(
        default=1.0,
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(5.0)
        ]
    )

    def __str__(self):
        return f"{self.rating} stars for {self.school_profile.school_name}"

class SchoolGallery(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='gallery_images/', blank=False, null=False)
    caption = models.CharField(max_length=255, blank=True, help_text="Optional caption for the image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.school_profile.school_name} - {self.caption or 'No caption'}"

class SchoolTestimonial(models.Model):
    school_profile = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='testimonials')
    author_name = models.CharField(max_length=100, blank=False, help_text="Name of the person giving the testimonial")
    author_role = models.CharField(
        max_length=50,
        choices=[
            ('parent', 'Parent'),
            ('student', 'Student'),
            ('alumni', 'Alumni'),
            ('teacher', 'Teacher'),
            ('other', 'Other'),
        ],
        blank=False,
        help_text="Role of the person giving the testimonial"
    )
    message = models.TextField(blank=False, help_text="The testimonial message")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.author_name} ({self.author_role}) for {self.school_profile.school_name}"