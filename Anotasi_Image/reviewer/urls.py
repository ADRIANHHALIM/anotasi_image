from django.urls import path
from . import views

app_name = "reviewer"

urlpatterns =[
    path('', views.home_reviewer, name='home_reviewer'),
    path('task_review/<int:id>/', views.task_review, name='task_review'),
    path('isu', views.isu, name='isu'),
    path('login', views.login, name='login'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('isu_image', views.isu_image, name='isu_image'),
    path('isu_anotasi', views.isu_anotasi, name='isu_anotasi'),
]