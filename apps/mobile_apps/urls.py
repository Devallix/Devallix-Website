from django.urls import path
from . import views

app_name = 'mobile_apps'

urlpatterns = [
    path('', views.MobileAppListView.as_view(), name='app_list'),
    path('<slug:slug>/', views.MobileAppDetailView.as_view(), name='app_detail'),
]
