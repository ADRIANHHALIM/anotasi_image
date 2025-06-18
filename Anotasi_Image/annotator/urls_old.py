from django.urls import path

app_name = 'annotator'

def temp_job_detail(request, job_id):
    # Import here to avoid circular import
    from .views import job_detail_view
    return job_detail_view(request, job_id)

def temp_annotate(request):
    from .views import annotate_view
    return annotate_view(request)

def temp_signin(request):
    from .views import signin_view
    return signin_view(request)

def temp_signout(request):
    from .views import signout_view
    return signout_view(request)

def temp_notifications(request):
    from .views import notifications_view
    return notifications_view(request)

urlpatterns = [
    path('', temp_annotate, name='home'),
    path('signin/', temp_signin, name='signin'),
    path('signout/', temp_signout, name='signout'),
    path('annotate/', temp_annotate, name='annotate'),
    path('job/<int:job_id>/', temp_job_detail, name='job_detail'),
    path('notifications/', temp_notifications, name='notifications'),
]
