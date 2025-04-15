from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import User

class CustomUserAdmin(UserAdmin):
    # Define the fields to display in the admin list view
    list_display = ('username', 'email', 'user_type', 'is_approved', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('user_type', 'is_approved', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Define the fieldsets for the add/edit form
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Check "Is Superuser" and set User Type to "Super Admin" for admin privileges.'
        }),
        ('Custom Fields', {'fields': ('user_type', 'is_approved')}),
    )

    # Define the fields for the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_approved', 'is_staff', 'is_superuser'),
            'description': 'For Super Admin, check "Is Superuser" and select "Super Admin" as User Type.'
        }),
    )

    # Override save_model to enforce super_admin role with is_superuser
    def save_model(self, request, obj, form, change):
        if obj.is_superuser and obj.user_type != 'super_admin':
            obj.user_type = 'super_admin'  # Automatically set to super_admin if is_superuser is checked
        super().save_model(request, obj, form, change)

    # Make user_type a required field in the add form
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:  # Add form
            return (
                (None, {'fields': ('username', 'email', 'password1', 'password2')}),
                ('Personal Info', {'fields': ('first_name', 'last_name')}),
                ('Permissions', {
                    'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
                    'description': 'Check "Is Superuser" and set User Type to "Super Admin" for admin privileges.'
                }),
                ('Custom Fields', {'fields': ('user_type', 'is_approved')}),
            )
        return fieldsets

# Register the User model with the custom admin class
admin.site.register(User, CustomUserAdmin)