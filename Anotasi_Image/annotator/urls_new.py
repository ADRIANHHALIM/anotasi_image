from django.urls import path
from django.http import JsonResponse

app_name = 'annotator'

# Import views one by one to avoid circular import
from .views import annotate_view, signin_view, signout_view, notifications_view

# Try to import accept_notification separately to debug
try:
    from .views import accept_notification
    print("DEBUG: accept_notification imported successfully")
except Exception as e:
    print(f"DEBUG: Failed to import accept_notification: {e}")
    # Create a dummy function as fallback
    def accept_notification(request, notification_id):
        return JsonResponse({'error': 'Function not available'}, status=500)

# Import job_detail_view separately
try:
    from .views import job_detail_view
except ImportError:
    # Fallback if import fails
    def job_detail_view(request, job_id):
        from django.http import HttpResponse
        return HttpResponse(f"Job {job_id} - Import Error")

urlpatterns = [
    path('', annotate_view, name='home'),
    path('signin/', signin_view, name='signin'),
    path('signout/', signout_view, name='signout'),
    path('annotate/', annotate_view, name='annotate'),
    path('job/<int:job_id>/', job_detail_view, name='job_detail'),
    path('notifications/', notifications_view, name='notifications'),
    path('accept-notification/<int:notification_id>/', accept_notification, name='accept_notification'),
]
