from django.urls import path
from . import views

app_name = 'graphic_design'

urlpatterns = [
    path('', views.DesignListView.as_view(), name='design_list'),
    path('<slug:slug>/', views.DesignDetailView.as_view(), name='design_detail'),
]
