from django.urls import path
from . import views

<<<<<<< HEAD
urlpatterns =[
    
]
=======
app_name = 'annotator'

urlpatterns = [
    # Main pages
    path('', views.annotate_view, name='home'),
    path('annotate/', views.annotate_view, name='annotate'),
    path('job/<int:job_id>/', views.job_detail_view, name='job_detail'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notification/<int:notification_id>/accept/', views.accept_notification_view, name='accept_notification'),
    
    # Authentication (if needed for annotator-specific auth)
    path('signin/', views.signin_view, name='signin'),
    path('signout/', views.signout_view, name='signout'),
]
>>>>>>> 25292504d23e7f8e25be5caa7222ee2190cf9cff
