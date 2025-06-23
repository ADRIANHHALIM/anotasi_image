from django.urls import path
from . import views

app_name = 'annotator'

urlpatterns = [
    path('', lambda request: get_view('annotate_view')(request), name='home'),
    path('signin/', lambda request: get_view('signin_view')(request), name='signin'),
    path('signout/', lambda request: get_view('signout_view')(request), name='signout'),
    path('annotate/', lambda request: get_view('annotate_view')(request), name='annotate'),
    path('job/<int:job_id>/', lambda request, job_id: get_view('job_detail_view')(request, job_id), name='job_detail'),
    path('notifications/', lambda request: get_view('notifications_view')(request), name='notifications'),
    path('accept-notification/<int:notification_id>/', lambda request, notification_id: get_view('accept_notification_view')(request, notification_id), name='accept_notification'),

]
