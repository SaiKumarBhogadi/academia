# Generated by Django 4.2.20 on 2025-03-27 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0007_testimonial_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schoolgallery',
            name='school_profile',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='school_profile',
        ),
        migrations.RemoveField(
            model_name='schoolrating',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='schoolrating',
            name='rating',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1),
        ),
        migrations.DeleteModel(
            name='BlogPost',
        ),
        migrations.DeleteModel(
            name='SchoolGallery',
        ),
        migrations.DeleteModel(
            name='Testimonial',
        ),
    ]
