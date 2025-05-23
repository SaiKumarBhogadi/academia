# Generated by Django 4.2.20 on 2025-05-03 08:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('profile_photo', models.ImageField(blank=True, null=True, upload_to='student_photos/')),
                ('nationality', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('General', 'General'), ('SC', 'SC'), ('ST', 'ST'), ('OBC', 'OBC'), ('Others', 'Others')], max_length=50)),
                ('aadhar_number', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('contact_number', models.CharField(max_length=15)),
                ('alternate_phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('street_address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('pincode', models.CharField(max_length=10)),
                ('father_name', models.CharField(max_length=100)),
                ('father_mobile', models.CharField(max_length=15)),
                ('father_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('mother_name', models.CharField(max_length=100)),
                ('mother_mobile', models.CharField(max_length=15)),
                ('mother_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('parent_income', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('admission_preference', models.CharField(choices=[('School', 'School'), ('College', 'College')], max_length=50)),
                ('desired_course', models.CharField(max_length=100)),
                ('last_institution', models.CharField(max_length=255)),
                ('previous_qualification', models.CharField(max_length=100)),
                ('marksheet', models.FileField(upload_to='student_documents/marksheets/')),
                ('transfer_certificate', models.FileField(upload_to='student_documents/certificates/')),
                ('entrance_score', models.FloatField(blank=True, null=True)),
                ('academic_year', models.CharField(max_length=20)),
                ('id_proof', models.FileField(upload_to='student_documents/id_proofs/')),
                ('caste_certificate', models.FileField(blank=True, null=True, upload_to='student_documents/caste_certificates/')),
                ('income_certificate', models.FileField(blank=True, null=True, upload_to='student_documents/income_certificates/')),
                ('passport_photo', models.ImageField(upload_to='student_photos/passport/')),
                ('signature', models.ImageField(upload_to='student_signatures/')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
