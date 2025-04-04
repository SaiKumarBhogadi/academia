from django.contrib import admin
from .models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'date_of_birth', 'gender', 'created_at')
    list_filter = ('gender',)
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    ordering = ('user__username',)
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'gender')}),
        ('Contact Info', {'fields': ('address', 'contact_number', 'email')}),
        ('Parent Info', {'fields': ('parent_name', 'parent_contact')}),
    )