from django.urls import path
from . import views
from .views import  activate

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path("activate/<uidb64>/<token>/", activate, name="activate"),  
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # path('create/', views.create_view, name='create'),
    path("home/", views.home_view, name="home"),
]
