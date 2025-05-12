from django.db import models
from core.models import User
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    )
    profile_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    nationality = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50,
        choices=[('General', 'General'), ('SC', 'SC'), ('ST', 'ST'), ('OBC', 'OBC'), ('Others', 'Others')]
    )
    aadhar_number = models.CharField(max_length=20)
    email = models.EmailField()
    contact_number = models.CharField(max_length=15)
    alternate_phone_number = models.CharField(max_length=15, blank=True, null=True)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    father_name = models.CharField(max_length=100)
    father_mobile = models.CharField(max_length=15)
    father_email = models.EmailField(blank=True, null=True)
    mother_name = models.CharField(max_length=100)
    mother_mobile = models.CharField(max_length=15)
    mother_email = models.EmailField(blank=True, null=True)
    parent_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    admission_preference = models.CharField(
        max_length=50,
        choices=[('School', 'School'), ('College', 'College')]
    )
    desired_course = models.CharField(max_length=100)
    last_institution = models.CharField(max_length=255)
    previous_qualification = models.CharField(max_length=100)
    marksheet = models.FileField(upload_to='student_documents/marksheets/')
    transfer_certificate = models.FileField(upload_to='student_documents/certificates/')
    entrance_score = models.FloatField(blank=True, null=True)
    academic_year = models.CharField(max_length=20)
    id_proof = models.FileField(upload_to='student_documents/id_proofs/')
    caste_certificate = models.FileField(upload_to='student_documents/caste_certificates/', blank=True, null=True)
    income_certificate = models.FileField(upload_to='student_documents/income_certificates/', blank=True, null=True)
    passport_photo = models.ImageField(upload_to='student_photos/passport/')
    signature = models.ImageField(upload_to='student_signatures/')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip() or "Unnamed Student"