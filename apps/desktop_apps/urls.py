from django.urls import path
from . import views

app_name = 'desktop_apps'

urlpatterns = [
    path('', views.AppListView.as_view(), name='app_list'),
    path('category/<slug:slug>/', views.CategoryAppListView.as_view(), name='category_detail'),
    path('<slug:slug>/', views.AppDetailView.as_view(), name='app_detail'),
    path('<slug:slug>/download/', views.download_app, name='download_app'),
]
