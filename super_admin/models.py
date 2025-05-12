from django.db import models

from django.db import models
from core.models import User

class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    role = models.CharField(max_length=20, choices=User.USER_TYPE_CHOICES)  # Uses User.USER_TYPE_CHOICES
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user.username} ({self.role}) - {self.action} at {self.timestamp}"