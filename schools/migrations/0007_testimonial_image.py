# Generated by Django 4.2.20 on 2025-03-27 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0006_testimonial_schoolrating_schoolgallery_blogpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='testimonial',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='testimonials/'),
        ),
    ]
