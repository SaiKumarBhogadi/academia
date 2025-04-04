# Generated by Django 4.2.20 on 2025-03-27 12:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0012_delete_schoolgallery'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='gallery/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('school_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gallery_images', to='schools.schoolprofile')),
            ],
        ),
    ]
