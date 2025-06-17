from django.urls import path
from . import views

app_name = 'annotator'

urlpatterns = [
    path('', views.annotate_view, name='home'),
    path('annotate/', views.annotate_view, name='annotate'),
    path('notifications/', views.notifications_view, name='notifications'),
]
