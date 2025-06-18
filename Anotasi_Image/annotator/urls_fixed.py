from django.urls import path
from django.http import JsonResponse, HttpResponse

app_name = 'annotator'

def accept_notification_view(request, notification_id):
    """
    Accept notification and update status to 'accepted'
    """
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)
        
    try:
        # Import here to avoid circular imports
        from master.models import Notification
        from django.utils import timezone
        from django.shortcuts import get_object_or_404
        
        # Check authentication
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=401)
        
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient=request.user
        )
        
        # Update notification status to accepted
        notification.status = 'accepted'
        notification.read_at = timezone.now()
        notification.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Notification accepted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def get_view(view_name):
    """Helper to import views dynamically"""
    from . import views
    return getattr(views, view_name)

urlpatterns = [
    path('', lambda request: get_view('annotate_view')(request), name='home'),
    path('signin/', lambda request: get_view('signin_view')(request), name='signin'),
    path('signout/', lambda request: get_view('signout_view')(request), name='signout'),
    path('annotate/', lambda request: get_view('annotate_view')(request), name='annotate'),
    path('job/<int:job_id>/', lambda request, job_id: get_view('job_detail_view')(request, job_id), name='job_detail'),
    path('notifications/', lambda request: get_view('notifications_view')(request), name='notifications'),
    path('accept-notification/<int:notification_id>/', accept_notification_view, name='accept_notification'),
]
