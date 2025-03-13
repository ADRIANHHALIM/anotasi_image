from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),  # ✅ Pastikan ada nama 'signup'
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create/', views.create_view, name='create'),
]
