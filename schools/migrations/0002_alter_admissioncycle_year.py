# Generated by Django 4.2.20 on 2025-04-16 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schools', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissioncycle',
            name='year',
            field=models.CharField(max_length=9),
        ),
    ]
