from django.contrib import admin
from .models import SchoolProfile, SchoolClass, ClassSection, Seat, Admission

@admin.register(SchoolProfile)
class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'user', 'city', 'state', 'school_type', 'created_at')
    list_filter = ('school_type', 'city', 'state', 'is_co_education', 'has_transport')
    search_fields = ('school_name', 'user__username', 'city', 'state')
    ordering = ('school_name',)
    fieldsets = (
        (None, {'fields': ('user', 'school_name')}),
        ('Address', {'fields': ('street_address', 'landmark', 'city', 'district', 'state', 'pincode', 'country')}),
        ('Contact Info', {'fields': ('contact_email', 'contact_phone')}),
        ('Details', {'fields': ('principal_name', 'accreditation', 'established_year', 'website', 'total_students', 'total_teachers')}),
        ('Profile', {'fields': ('profile_pic', 'school_type', 'medium_of_instruction', 'start_grade', 'end_grade', 'is_co_education')}),
        ('Additional Info', {'fields': ('facilities', 'has_transport', 'school_motto', 'affiliation_number')}),
    )

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('grade', 'school', 'total_sections')
    list_filter = ('school',)
    search_fields = ('grade', 'school__school_name')
    ordering = ('grade',)

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'section_name', 'total_seats', 'filled_seats', 'available_seats')
    list_filter = ('school_class__school', 'school_class__grade')
    search_fields = ('section_name', 'school_class__grade', 'school_class__school__school_name')
    ordering = ('school_class__grade', 'section_name')

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'section', 'is_filled', 'student')
    list_filter = ('is_filled', 'section__school_class__school')
    search_fields = ('seat_number', 'section__section_name', 'student__username')
    ordering = ('section', 'seat_number')

@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('admission_id', 'student', 'school', 'school_class', 'section', 'status', 'admission_date')  # Added admission_id
    list_filter = ('status', 'school', 'school_class__grade', 'section__section_name')
    search_fields = ('admission_id', 'student__username', 'school__school_name')  # Added admission_id
    ordering = ('-admission_date',)
    fieldsets = (
        (None, {'fields': ('school', 'student', 'admission_id')}),  # Added admission_id
        ('Class Info', {'fields': ('school_class', 'section', 'seat')}),
        ('Parent Info', {'fields': ('parent_name', 'contact_number', 'email')}),
        ('Status', {'fields': ('status', 'admission_date')}),
    )