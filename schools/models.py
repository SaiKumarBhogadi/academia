from django.db import models
from core.models import User  # Ensure we're importing your custom User model

# School Profile Model
class SchoolProfile(models.Model):
    SCHOOL_TYPE_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('international', 'International'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='school_profile')
    school_name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, default="India", blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    principal_name = models.CharField(max_length=100, blank=True, null=True)
    accreditation = models.CharField(max_length=100, blank=True, null=True)
    established_year = models.PositiveIntegerField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    total_students = models.PositiveIntegerField(blank=True, null=True)
    total_teachers = models.PositiveIntegerField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='school_profiles/', blank=True, null=True)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES, blank=True, null=True)
    medium_of_instruction = models.CharField(max_length=50, blank=True, null=True)
    start_grade = models.PositiveIntegerField(blank=True, null=True)
    end_grade = models.PositiveIntegerField(blank=True, null=True)
    is_co_education = models.BooleanField(default=True)
    facilities = models.TextField(blank=True, null=True)
    has_transport = models.BooleanField(default=False)
    school_motto = models.CharField(max_length=255, blank=True, null=True)
    affiliation_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.school_name}"

# SchoolClass Model
class SchoolClass(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='classes')
    grade = models.CharField(max_length=50)
    total_sections = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.grade} - {self.school.school_name}"

# ClassSection Model
class ClassSection(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='sections')
    section_name = models.CharField(max_length=10)
    total_seats = models.PositiveIntegerField(default=40)
    filled_seats = models.PositiveIntegerField(default=0)

    def available_seats(self):
        return self.total_seats - self.filled_seats

    def __str__(self):
        return f"{self.school_class.grade} - {self.section_name}"

# Seat Model
class Seat(models.Model):
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=10)
    is_filled = models.BooleanField(default=False)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='seats')

    def __str__(self):
        return f"{self.section} - Seat {self.seat_number}"


class Admission(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Withdrawn', 'Withdrawn'),
    ]

    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE, related_name='admissions')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='admissions')
    section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='admissions')
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE, related_name='admission', null=True)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admissions', null=True)
    parent_name = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admission_id = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        # Call the parent save method first to set admission_date
        if not self.pk:  # Only for new objects
            super().save(*args, **kwargs)  # This sets admission_date due to auto_now_add=True

        # Now generate admission_id if it doesn't exist
        if not self.admission_id:
            year = self.admission_date.year
            last_admission = Admission.objects.filter(admission_id__startswith=f"ADM-{year}-").order_by('-admission_id').first()
            if last_admission:
                last_number = int(last_admission.admission_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.admission_id = f"ADM-{year}-{new_number:03d}"

        # Save again to update admission_id
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username if self.student else 'No Student'} - {self.section}"
    

from django.core.validators import MinValueValidator, MaxValueValidator
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
    

# Add this to your existing models.py
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