# Generated by Django 4.2.20 on 2025-04-12 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0004_alter_admissioncycle_options_alter_course_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='degree',
            unique_together={('college', 'cycle', 'name')},
        ),
    ]
