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
]