from django.urls import path
from . import views
from .views import activate

app_name = 'master'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path("activate/<uidb64>/<token>/", activate, name="activate"),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("home/", views.home_view, name="home"),
    path("assign_roles/", views.assign_roles_view, name="assign_roles"),
    path("job_settings/", views.job_settings_view, name="job_settings"),
    path("issue_solving/", views.issue_solving_view, name="issue_solving"),
    path("performance/", views.performance_view, name="performance"),
    path("process_validations/", views.process_validation_view, name="process_validations"),
    
    # Update Role
    path("update_role/", views.update_role, name="update_role"),
    path("add_dataset/", views.add_dataset_view, name="add_dataset"),
    
    # Job Settings
    path('create_job_profile/', views.create_job_profile, name='create_job_profile'),
    path('job-profile/<int:job_id>/', views.job_profile_detail, name='job_profile_detail'),
    path('upload-job-images/', views.upload_job_images, name='upload_job_images'),
    
    # Home Dataset 
    path('edit_dataset/<int:dataset_id>/', views.edit_dataset_view, name='edit_dataset'),
    path('delete_dataset/<int:dataset_id>/', views.delete_dataset_view, name='delete_dataset'),
    
    # New URLs
    path('get-workers/<str:role>/', views.get_workers, name='get_workers'),
    path('assign-worker/', views.assign_worker, name='assign_worker'),
]