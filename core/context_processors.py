from core.models import Notification

def notifications(request):
    if request.user.is_authenticated:
        # Fetch the last 5 notifications (read or unread) for the user
        user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        # Count unread notifications for the badge
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        user_notifications = []
        unread_count = 0

    return {
        'notifications': user_notifications,
        'unread_notifications_count': unread_count,
    }