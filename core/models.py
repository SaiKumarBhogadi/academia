from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('school', 'School'),
        ('college', 'College'),
        ('super_admin', 'Super Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    is_approved = models.BooleanField(default=False)

    # Override the email field to make it unique
    email = models.EmailField(unique=True, error_messages={
        'unique': "A user with that email already exists.",
    })

    def __str__(self):
        return self.username
    

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('password_change', 'Password Change'),
        ('admission_update', 'Admission Update'),
        ('profile_update', 'Profile Update'),
        ('general', 'General'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"