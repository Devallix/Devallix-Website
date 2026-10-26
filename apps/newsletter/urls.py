from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='subscribe'),
]
