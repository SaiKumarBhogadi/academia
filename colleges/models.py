# colleges/models.py
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

class Degree(models.Model):
    college = models.ForeignKey(CollegeProfile, on_delete=models.CASCADE, related_name='degrees')
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    eligibility_criteria = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Degree"
        verbose_name_plural = "Degrees"

class Department(models.Model):
    college = models.ForeignKey(CollegeProfile, on_delete=models.CASCADE, related_name='departments')
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    hod_name = models.CharField(max_length=100, blank=True)
    faculty_count = models.PositiveIntegerField(default=0)
    labs = models.TextField(blank=True)
    total_seats = models.PositiveIntegerField()
    fees_per_year = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.degree.name} ({self.college.college_name})"

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"

class Course(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='courses')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    semester = models.CharField(max_length=20)
    credits = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course_code} - {self.name} ({self.degree.name})"

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"