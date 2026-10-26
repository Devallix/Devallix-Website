from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    FormView,
    TemplateView,
    UpdateView,
)
from .forms import (
    UserLoginForm,
    UserRegistrationForm,
    UserProfileForm,
    UserPasswordChangeForm,
    UserPasswordResetForm,
    UserSetPasswordForm,
)
from .models import Profile


class UserLoginView(SuccessMessageMixin, FormView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    success_message = 'You have been logged in successfully.'
    success_url = reverse_lazy('dashboard:dashboard_home')

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard_home')
        return super().dispatch(request, *args, **kwargs)


class UserLogoutView(TemplateView):
    template_name = 'accounts/logout.html'

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('core:home')


class UserRegisterView(SuccessMessageMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_message = 'Account created successfully. Please log in.'
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard_home')
        return super().dispatch(request, *args, **kwargs)


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        return context


class UserProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_message = 'Profile updated successfully.'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_message = 'Password changed successfully.'
    success_url = reverse_lazy('accounts:profile')


class UserPasswordResetView(SuccessMessageMixin, PasswordResetView):
    form_class = UserPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_message = 'Password reset email sent. Please check your inbox.'
    success_url = reverse_lazy('accounts:login')


class UserPasswordResetConfirmView(SuccessMessageMixin, PasswordResetConfirmView):
    form_class = UserSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_message = 'Password reset successful. Please log in with your new password.'
    success_url = reverse_lazy('accounts:login')
