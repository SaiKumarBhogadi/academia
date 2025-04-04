from core.models import Notification

def create_notification(user, message, notification_type='general'):
    """
    Create a notification for a user.
    
    Args:
        user: The user to send the notification to.
        message: The notification message.
        notification_type: The type of notification (e.g., 'password_change').
    """
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type
    )