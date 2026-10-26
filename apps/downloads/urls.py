from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('', views.DownloadListView.as_view(), name='download_list'),
]
