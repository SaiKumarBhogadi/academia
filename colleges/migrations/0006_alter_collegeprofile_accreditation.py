# Generated by Django 4.2.20 on 2025-05-09 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0005_collegeprofile_district_alter_collegeprofile_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collegeprofile',
            name='accreditation',
            field=models.CharField(choices=[('AICTE', 'AICTE'), ('NAAC', 'NAAC'), ('NBA', 'NBA'), ('', 'Other')], max_length=100),
        ),
    ]
