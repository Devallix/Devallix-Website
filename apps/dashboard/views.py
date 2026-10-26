from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponse
from apps.desktop_apps.models import DesktopApplication, ApplicationVersion, ApplicationCategory, Screenshot
from apps.web_projects.models import WebProject
from apps.mobile_apps.models import MobileApp
from apps.graphic_design.models import GraphicDesignProject
from apps.portfolio.models import Skill, SkillCategory, Technology
from apps.blog.models import BlogPost, BlogCategory, Tag, Comment
from apps.contact.models import ContactMessage
from apps.testimonials.models import Testimonial
from apps.newsletter.models import NewsletterSubscriber, Newsletter
from apps.downloads.models import Download
from apps.accounts.models import Profile
from .forms import AppForm, VersionForm, ProjectForm, SkillForm, BlogPostForm, TestimonialForm, CategoryForm, SiteSettingsForm, MobileAppForm, GraphicDesignForm


class DashboardLoginRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'accounts:login'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


class DashboardHomeView(DashboardLoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_apps'] = DesktopApplication.objects.count()
        context['total_projects'] = WebProject.objects.count()
        context['total_mobile_apps'] = MobileApp.objects.count()
        context['total_designs'] = GraphicDesignProject.objects.count()
        context['total_downloads'] = Download.objects.count()
        context['total_messages'] = ContactMessage.objects.count()
        context['unread_messages'] = ContactMessage.objects.filter(status='unread').count()
        context['total_subscribers'] = NewsletterSubscriber.objects.filter(is_active=True).count()
        context['total_posts'] = BlogPost.objects.count()
        context['total_testimonials'] = Testimonial.objects.count()
        context['recent_messages'] = ContactMessage.objects.all()[:5]
        context['recent_downloads'] = Download.objects.select_related('application').all()[:5]
        context['recent_subscribers'] = NewsletterSubscriber.objects.all()[:5]
        context['app_download_stats'] = DesktopApplication.objects.filter(
            published=True
        ).order_by('-download_count')[:5]
        context['total_app_downloads'] = DesktopApplication.objects.aggregate(
            total=Sum('download_count')
        )['total'] or 0
        return context


class AppListView(DashboardLoginRequiredMixin, ListView):
    model = DesktopApplication
    template_name = 'dashboard/app_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        qs = DesktopApplication.objects.all()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class AppCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = DesktopApplication
    template_name = 'dashboard/app_form.html'
    form_class = AppForm
    success_url = reverse_lazy('dashboard:app_list')
    success_message = 'Application created successfully.'

    def form_valid(self, form):
        form.instance.developer = self.request.user.get_full_name() or self.request.user.username
        return super().form_valid(form)


class AppUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = DesktopApplication
    template_name = 'dashboard/app_form.html'
    form_class = AppForm
    success_url = reverse_lazy('dashboard:app_list')
    success_message = 'Application updated successfully.'


class AppDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = DesktopApplication
    template_name = 'dashboard/app_confirm_delete.html'
    success_url = reverse_lazy('dashboard:app_list')
    success_message = 'Application deleted successfully.'


class VersionCreateView(DashboardLoginRequiredMixin, CreateView):
    model = ApplicationVersion
    template_name = 'dashboard/version_form.html'
    form_class = VersionForm
    success_message = 'Version added successfully.'

    def form_valid(self, form):
        form.instance.application = get_object_or_404(DesktopApplication, pk=self.kwargs['app_pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboard:app_detail', kwargs={'pk': self.kwargs['app_pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = get_object_or_404(DesktopApplication, pk=self.kwargs['app_pk'])
        return context


class AppDetailView(DashboardLoginRequiredMixin, TemplateView):
    template_name = 'dashboard/app_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['application'] = get_object_or_404(DesktopApplication, pk=self.kwargs['pk'])
        context['versions'] = ApplicationVersion.objects.filter(application=context['application'])
        context['screenshots'] = Screenshot.objects.filter(application=context['application'])
        return context


from django.views import View


class ScreenshotUploadView(DashboardLoginRequiredMixin, View):
    def post(self, request, pk):
        app = get_object_or_404(DesktopApplication, pk=pk)
        images = request.FILES.getlist('images')
        for i, image in enumerate(images):
            Screenshot.objects.create(
                application=app,
                image=image,
                display_order=i,
            )
        messages.success(request, f'{len(images)} screenshot(s) uploaded.')
        return redirect('dashboard:app_detail', pk=pk)


class ScreenshotDeleteView(DashboardLoginRequiredMixin, View):
    def post(self, request, pk):
        screenshot = get_object_or_404(Screenshot, pk=pk)
        app_pk = screenshot.application.pk
        screenshot.image.delete()
        screenshot.delete()
        messages.success(request, 'Screenshot deleted.')
        return redirect('dashboard:app_detail', pk=app_pk)


class ProjectListView(DashboardLoginRequiredMixin, ListView):
    model = WebProject
    template_name = 'dashboard/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20

    def get_queryset(self):
        qs = WebProject.objects.all()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class ProjectCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = WebProject
    template_name = 'dashboard/project_form.html'
    form_class = ProjectForm
    success_url = reverse_lazy('dashboard:project_list')
    success_message = 'Project created successfully.'


class ProjectUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = WebProject
    template_name = 'dashboard/project_form.html'
    form_class = ProjectForm
    success_url = reverse_lazy('dashboard:project_list')
    success_message = 'Project updated successfully.'


class ProjectDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = WebProject
    template_name = 'dashboard/project_confirm_delete.html'
    success_url = reverse_lazy('dashboard:project_list')
    success_message = 'Project deleted successfully.'


class MobileAppListView(DashboardLoginRequiredMixin, ListView):
    model = MobileApp
    template_name = 'dashboard/mobile_app_list.html'
    context_object_name = 'mobile_apps'
    paginate_by = 20

    def get_queryset(self):
        qs = MobileApp.objects.all()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class MobileAppCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MobileApp
    template_name = 'dashboard/mobile_app_form.html'
    form_class = MobileAppForm
    success_url = reverse_lazy('dashboard:mobile_app_list')
    success_message = 'Mobile app created successfully.'


class MobileAppUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MobileApp
    template_name = 'dashboard/mobile_app_form.html'
    form_class = MobileAppForm
    success_url = reverse_lazy('dashboard:mobile_app_list')
    success_message = 'Mobile app updated successfully.'


class MobileAppDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = MobileApp
    template_name = 'dashboard/mobile_app_confirm_delete.html'
    success_url = reverse_lazy('dashboard:mobile_app_list')
    success_message = 'Mobile app deleted successfully.'


class DesignListView(DashboardLoginRequiredMixin, ListView):
    model = GraphicDesignProject
    template_name = 'dashboard/design_list.html'
    context_object_name = 'designs'
    paginate_by = 20

    def get_queryset(self):
        qs = GraphicDesignProject.objects.all()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class DesignCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = GraphicDesignProject
    template_name = 'dashboard/design_form.html'
    form_class = GraphicDesignForm
    success_url = reverse_lazy('dashboard:design_list')
    success_message = 'Graphic design project created successfully.'


class DesignUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = GraphicDesignProject
    template_name = 'dashboard/design_form.html'
    form_class = GraphicDesignForm
    success_url = reverse_lazy('dashboard:design_list')
    success_message = 'Graphic design project updated successfully.'


class DesignDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = GraphicDesignProject
    template_name = 'dashboard/design_confirm_delete.html'
    success_url = reverse_lazy('dashboard:design_list')
    success_message = 'Graphic design project deleted successfully.'


class SkillListView(DashboardLoginRequiredMixin, ListView):
    model = Skill
    template_name = 'dashboard/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 20


class SkillCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Skill
    template_name = 'dashboard/skill_form.html'
    form_class = SkillForm
    success_url = reverse_lazy('dashboard:skill_list')
    success_message = 'Skill created successfully.'


class SkillUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Skill
    template_name = 'dashboard/skill_form.html'
    form_class = SkillForm
    success_url = reverse_lazy('dashboard:skill_list')
    success_message = 'Skill updated successfully.'


class SkillDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = Skill
    template_name = 'dashboard/skill_confirm_delete.html'
    success_url = reverse_lazy('dashboard:skill_list')
    success_message = 'Skill deleted successfully.'


class BlogPostListView(DashboardLoginRequiredMixin, ListView):
    model = BlogPost
    template_name = 'dashboard/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        qs = BlogPost.objects.all()
        search = self.request.GET.get('q')
        status = self.request.GET.get('status')
        if search:
            qs = qs.filter(title__icontains=search)
        if status:
            qs = qs.filter(status=status)
        return qs


class BlogPostCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogPost
    template_name = 'dashboard/blog_form.html'
    form_class = BlogPostForm
    success_url = reverse_lazy('dashboard:blog_list')
    success_message = 'Blog post created successfully.'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.status == 'published':
            from django.utils import timezone
            form.instance.published_at = timezone.now()
        return super().form_valid(form)


class BlogPostUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BlogPost
    template_name = 'dashboard/blog_form.html'
    form_class = BlogPostForm
    success_url = reverse_lazy('dashboard:blog_list')
    success_message = 'Blog post updated successfully.'


class BlogPostDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'dashboard/blog_confirm_delete.html'
    success_url = reverse_lazy('dashboard:blog_list')
    success_message = 'Blog post deleted successfully.'


class MessageListView(DashboardLoginRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'dashboard/message_list.html'
    context_object_name = 'messages_list'
    paginate_by = 20

    def get_queryset(self):
        qs = ContactMessage.objects.all()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class MessageDetailView(DashboardLoginRequiredMixin, TemplateView):
    template_name = 'dashboard/message_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message'] = get_object_or_404(ContactMessage, pk=self.kwargs['pk'])
        return context


class MessageActionView(DashboardLoginRequiredMixin, View):
    def post(self, request, pk):
        msg = get_object_or_404(ContactMessage, pk=pk)
        action = request.POST.get('action')
        if action == 'read':
            msg.mark_read()
        elif action == 'replied':
            msg.mark_replied()
        elif action == 'archive':
            msg.archive()
        elif action == 'delete':
            msg.delete()
            messages.success(request, 'Message deleted.')
            return redirect('dashboard:message_list')
        messages.success(request, f'Message marked as {action}.')
        return redirect('dashboard:message_detail', pk=pk)


class TestimonialListView(DashboardLoginRequiredMixin, ListView):
    model = Testimonial
    template_name = 'dashboard/testimonial_list.html'
    context_object_name = 'testimonials'
    paginate_by = 20


class TestimonialCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Testimonial
    template_name = 'dashboard/testimonial_form.html'
    form_class = TestimonialForm
    success_url = reverse_lazy('dashboard:testimonial_list')
    success_message = 'Testimonial created successfully.'


class TestimonialUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Testimonial
    template_name = 'dashboard/testimonial_form.html'
    form_class = TestimonialForm
    success_url = reverse_lazy('dashboard:testimonial_list')
    success_message = 'Testimonial updated successfully.'


class TestimonialDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = Testimonial
    template_name = 'dashboard/testimonial_confirm_delete.html'
    success_url = reverse_lazy('dashboard:testimonial_list')
    success_message = 'Testimonial deleted successfully.'


class SubscriberListView(DashboardLoginRequiredMixin, ListView):
    model = NewsletterSubscriber
    template_name = 'dashboard/subscriber_list.html'
    context_object_name = 'subscribers'
    paginate_by = 20


class SubscriberExportView(DashboardLoginRequiredMixin, View):
    def get(self, request):
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Name', 'Active', 'Subscribed At'])
        for sub in NewsletterSubscriber.objects.all():
            writer.writerow([sub.email, sub.name, sub.is_active, sub.created_at])
        return response


class CategoryListView(DashboardLoginRequiredMixin, ListView):
    model = ApplicationCategory
    template_name = 'dashboard/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20


class CategoryCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ApplicationCategory
    template_name = 'dashboard/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('dashboard:category_list')
    success_message = 'Category created successfully.'


class CategoryUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ApplicationCategory
    template_name = 'dashboard/category_form.html'
    form_class = CategoryForm
    success_url = reverse_lazy('dashboard:category_list')
    success_message = 'Category updated successfully.'


class CategoryDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = ApplicationCategory
    template_name = 'dashboard/category_confirm_delete.html'
    success_url = reverse_lazy('dashboard:category_list')
    success_message = 'Category deleted successfully.'


class DownloadStatsView(DashboardLoginRequiredMixin, TemplateView):
    template_name = 'dashboard/download_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_downloads'] = Download.objects.count()
        context['app_downloads'] = DesktopApplication.objects.filter(
            published=True
        ).order_by('-download_count')[:10]
        context['recent_downloads'] = Download.objects.select_related(
            'application', 'version'
        ).all()[:20]
        return context


class SiteSettingsView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiteSettingsForm
    template_name = 'dashboard/site_settings.html'
    success_url = reverse_lazy('dashboard:site_settings')
    success_message = 'Site settings updated successfully.'

    def get_object(self, queryset=None):
        from apps.core.models import SiteSettings
        return SiteSettings.load()
