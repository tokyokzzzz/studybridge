from .models import ConnectionRequest, Message


def dashboard_context(request):
    if request.user.is_authenticated:
        pending_count = ConnectionRequest.objects.filter(
            to_user=request.user, status='pending'
        ).count()
        unread_count = Message.objects.filter(
            receiver=request.user, is_read=False
        ).count()
        return {
            'pending_requests_count': pending_count,
            'unread_messages_count': unread_count,
        }
    return {'pending_requests_count': 0, 'unread_messages_count': 0}
