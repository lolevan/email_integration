from django.urls import path

from . import views

urlpatterns = [
    path('', views.email_list, name='email_list'),
    path('fetch_emails/', views.fetch_emails, name='fetch_emails'),
]
