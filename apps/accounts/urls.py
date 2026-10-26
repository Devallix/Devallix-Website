from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/edit/', views.UserProfileUpdateView.as_view(), name='profile_edit'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
