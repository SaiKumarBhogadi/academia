# Generated by Django 4.2.20 on 2025-04-12 06:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('colleges', '0003_alter_department_unique_together_degree_cycle'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='admissioncycle',
            options={},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={},
        ),
        migrations.AlterModelOptions(
            name='degree',
            options={},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='admissioncycle',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='college',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='colleges.collegeprofile'),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='start_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='admissioncycle',
            name='year',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
