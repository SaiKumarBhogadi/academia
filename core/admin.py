from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin list view
    list_display = ('username', 'email', 'user_type', 'is_approved', 'is_active')
    list_filter = ('user_type', 'is_approved', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Define the fieldsets for the add/edit form
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Custom Fields', {'fields': ('user_type', 'is_approved')}),
    )

    # Define the fields for the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_approved'),
        }),
    )

# Register the User model with the custom admin class
admin.site.register(User, CustomUserAdmin)