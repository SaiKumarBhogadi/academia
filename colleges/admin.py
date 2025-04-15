# colleges/admin.py
from django.contrib import admin
from .models import CollegeProfile, Department, Degree, Course , Section

@admin.register(CollegeProfile)
class CollegeProfileAdmin(admin.ModelAdmin):
    list_display = ('college_name', 'college_type', 'contact_email', 'degree_count')
    list_filter = ('college_type',)
    search_fields = ('college_name', 'contact_email')

    def degree_count(self, obj):
        return obj.degrees.count()
    degree_count.short_description = 'Number of Degrees'

@admin.register(Degree)
class DegreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'duration')
    list_filter = ('college',)
    search_fields = ('name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'college', 'degree', 'hod_name', 'faculty_count',  'fees_per_year')
    list_filter = ('college', 'degree')
    search_fields = ('name', 'hod_name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'name', 'degree', 'department', 'semester', 'credits')
    list_filter = ('degree', 'department')
    search_fields = ('course_code', 'name')

admin.site.register(Section)