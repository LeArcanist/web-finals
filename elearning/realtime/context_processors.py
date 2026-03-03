from .models import Notification

def notifications_sidebar(request):
    if not request.user.is_authenticated:
        return {}

    latest = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:10]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

    return {
        "sidebar_notifications": latest,
        "sidebar_unread_count": unread_count,
    }