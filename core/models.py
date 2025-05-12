from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

class CustomUserManager(UserManager):
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('user_type', 'super_admin')
        extra_fields.setdefault('is_approved', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not username:
            raise ValueError('The username must be set')
        if not email:
            raise ValueError('The email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('school', 'School'),
        ('college', 'College'),
        ('super_admin', 'Super Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')
    is_approved = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    password_reset_requested_at = models.DateTimeField(null=True, blank=True)
    password_reset_created_at = models.DateTimeField(null=True, blank=True)

    email = models.EmailField(unique=True, error_messages={
        'unique': "A user with that email already exists.",
    })

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def is_super_admin(self):
        return self.user_type == 'super_admin'

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