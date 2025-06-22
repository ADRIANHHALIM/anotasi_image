from django.urls import path
from . import views

app_name = 'annotator'

urlpatterns = [
    # Main pages
    path('', views.annotate_view, name='home'),
    path('annotate/', views.annotate_view, name='annotate'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    
    # Notifications
    path('notifications/', views.notification_view, name='notifications'),
    path('notification/<int:notification_id>/accept/', views.accept_notification, name='accept_notification'),
    
    # Authentication (if needed for annotator-specific auth)
    path('signin/', views.signin_view, name='signin'),
    path('signout/', views.signout_view, name='signout'),
]