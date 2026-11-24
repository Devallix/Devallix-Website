from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
)
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse, HttpResponse
from apps.desktop_apps.models import DesktopApplication, ApplicationVersion, ApplicationCategory, Screenshot
from apps.web_projects.models import WebProject
from apps.mobile_apps.models import MobileApp
from apps.graphic_design.models import GraphicDesignProject
from apps.portfolio.models import Skill, SkillCategory, Technology
from apps.blog.models import BlogPost, BlogCategory, Tag, Comment, BlogSubCategory, PostLike
from apps.contact.models import ContactMessage
from apps.testimonials.models import Testimonial
from apps.newsletter.models import NewsletterSubscriber, Newsletter
from apps.downloads.models import Download
from apps.accounts.models import Profile
from .forms import (
    AppForm, VersionForm, ProjectForm, SkillForm, BlogPostForm,
    TestimonialForm, CategoryForm, SiteSettingsForm, MobileAppForm,
    GraphicDesignForm, BlogCategoryForm, BlogSubCategoryForm
)


class DashboardLoginRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'accounts:login'

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff


def _percent_change(current, previous):
    """Return a signed percentage change, or None when there is no baseline."""
    if previous <= 0:
        return 100.0 if current > 0 else None
    return round(((current - previous) / previous) * 100, 1)


def _activity_item(kind, icon, title, description, timestamp, url, color):
    return {
        'kind': kind,
        'icon': icon,
        'title': title,
        'description': description,
        'timestamp': timestamp,
        'url': url,
        'color': color,
    }


class DashboardHomeView(DashboardLoginRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        apps = list(DesktopApplication.objects.all())
        published_apps = [app for app in apps if app.published]
        message_stats = ContactMessage.objects.aggregate(
            total=Count('id'), unread=Count('id', filter=Q(status='unread'))
        )
        comment_stats = Comment.objects.aggregate(
            total=Count('id'), pending=Count('id', filter=Q(is_approved=False))
        )

        context['total_apps'] = len(apps)
        context['total_projects'] = WebProject.objects.count()
        context['total_mobile_apps'] = MobileApp.objects.count()
        context['total_designs'] = GraphicDesignProject.objects.count()
        context['total_downloads'] = Download.objects.count()
        context['total_messages'] = message_stats['total']
        context['unread_messages'] = message_stats['unread']
        context['total_subscribers'] = NewsletterSubscriber.objects.filter(
            is_active=True
        ).count()
        context['total_posts'] = BlogPost.objects.count()
        context['total_comments'] = comment_stats['total']
        context['pending_comments'] = comment_stats['pending']
        context['total_testimonials'] = Testimonial.objects.count()
        context['recent_messages'] = ContactMessage.objects.all()[:5]
        context['recent_downloads'] = Download.objects.select_related(
            'application'
        ).all()[:5]
        context['recent_subscribers'] = NewsletterSubscriber.objects.all()[:5]
        context['app_download_stats'] = sorted(
            published_apps, key=lambda app: (-app.download_count, app.name)
        )[:5]
        context['total_app_downloads'] = sum(app.download_count for app in apps)
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
    context_object_name = 'application'
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
    context_object_name = 'project'
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
    context_object_name = 'mobileapp'
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
    context_object_name = 'graphicdesignproject'
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
    context_object_name = 'skill'
    success_url = reverse_lazy('dashboard:skill_list')
    success_message = 'Skill deleted successfully.'


class BlogPostListView(DashboardLoginRequiredMixin, ListView):
    model = BlogPost
    template_name = 'dashboard/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 15

    def get_queryset(self):
        qs = (
            BlogPost.objects.select_related('author', 'category')
            .annotate(
                likes_count_annotation=Count('likes', distinct=True),
                approved_comments_count_annotation=Count(
                    'comments', filter=Q(comments__is_approved=True), distinct=True
                ),
            )
            .order_by('-published_at', '-created_at')
        )
        search = self.request.GET.get('search') or self.request.GET.get('q')
        status = self.request.GET.get('status')
        category = self.request.GET.get('category')
        if search:
            qs = qs.filter(title__icontains=search)
        if status:
            qs = qs.filter(status=status)
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.annotate(posts_count=Count('posts')).order_by('display_order', 'name')
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search') or self.request.GET.get('q') or ''
        context['selected_status'] = self.request.GET.get('status', '')
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['useful_websites_category_id'] = (
            BlogCategory.objects.filter(is_useful_websites_directory=True)
            .values_list('id', flat=True).first()
        )
        return context


class BlogPostUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BlogPost
    template_name = 'dashboard/blog_form.html'
    form_class = BlogPostForm
    success_url = reverse_lazy('dashboard:blog_list')
    success_message = 'Blog post updated successfully.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['useful_websites_category_id'] = (
            BlogCategory.objects.filter(is_useful_websites_directory=True)
            .values_list('id', flat=True).first()
        )
        return context


class BlogPostDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'dashboard/blog_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('dashboard:blog_list')
    success_message = 'Blog post deleted successfully.'


class BlogCategoryListView(DashboardLoginRequiredMixin, ListView):
    model = BlogCategory
    template_name = 'dashboard/blog_category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = BlogCategory.objects.annotate(posts_count=Count('posts')).order_by('display_order', 'name')
        search = self.request.GET.get('search') or self.request.GET.get('q')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search') or self.request.GET.get('q') or ''
        context['subcategories'] = BlogSubCategory.objects.select_related('category').annotate(
            posts_count=Count('posts')
        ).order_by('display_order', 'name')
        return context


class BlogCategoryCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogCategory
    template_name = 'dashboard/blog_category_form.html'
    form_class = BlogCategoryForm
    success_url = reverse_lazy('dashboard:blog_category_list')
    success_message = 'Blog category created successfully.'

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'name': self.object.name,
                'slug': self.object.slug,
                'message': 'Category created successfully.'
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: [str(err) for err in error_list] for field, error_list in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)
        return super().form_invalid(form)


class BlogCategoryUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BlogCategory
    template_name = 'dashboard/blog_category_form.html'
    form_class = BlogCategoryForm
    success_url = reverse_lazy('dashboard:blog_category_list')
    success_message = 'Blog category updated successfully.'


class BlogCategoryDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = BlogCategory
    template_name = 'dashboard/blog_category_confirm_delete.html'
    context_object_name = 'category'
    success_url = reverse_lazy('dashboard:blog_category_list')
    success_message = 'Blog category deleted successfully.'


class BlogSubCategoryListView(DashboardLoginRequiredMixin, ListView):
    model = BlogSubCategory
    template_name = 'dashboard/blog_subcategory_list.html'
    context_object_name = 'subcategories'
    paginate_by = 20

    def get_queryset(self):
        qs = BlogSubCategory.objects.select_related('category').all()
        search = self.request.GET.get('search') or self.request.GET.get('q')
        category = self.request.GET.get('category')
        if search:
            qs = qs.filter(name__icontains=search)
        if category:
            qs = qs.filter(category__slug=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search') or self.request.GET.get('q') or ''
        context['selected_category'] = self.request.GET.get('category', '')
        context['categories'] = BlogCategory.objects.all()
        return context


class BlogSubCategoryCreateView(DashboardLoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = BlogSubCategory
    template_name = 'dashboard/blog_subcategory_form.html'
    form_class = BlogSubCategoryForm
    success_url = reverse_lazy('dashboard:blog_subcategory_list')
    success_message = 'Blog sub-category created successfully.'


class BlogSubCategoryUpdateView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = BlogSubCategory
    template_name = 'dashboard/blog_subcategory_form.html'
    form_class = BlogSubCategoryForm
    success_url = reverse_lazy('dashboard:blog_subcategory_list')
    success_message = 'Blog sub-category updated successfully.'


class BlogSubCategoryDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = BlogSubCategory
    template_name = 'dashboard/blog_subcategory_confirm_delete.html'
    context_object_name = 'subcategory'
    success_url = reverse_lazy('dashboard:blog_subcategory_list')
    success_message = 'Blog sub-category deleted successfully.'


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
    context_object_name = 'testimonial'
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
        for sub in NewsletterSubscriber.objects.all().iterator():
            writer.writerow([sub.email, sub.name, sub.is_active, sub.created_at])
        return response


class CategoryListView(DashboardLoginRequiredMixin, ListView):
    model = ApplicationCategory
    template_name = 'dashboard/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        return ApplicationCategory.objects.annotate(
            applications_count=Count('applications')
        )


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
    context_object_name = 'category'
    success_url = reverse_lazy('dashboard:category_list')
    success_message = 'Category deleted successfully.'


class DownloadStatsView(DashboardLoginRequiredMixin, TemplateView):
    """Site-wide analytics built from recorded portfolio activity."""

    template_name = 'dashboard/download_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Use datetime bounds instead of __date lookups so SQLite can use the
        # downloaded_at/created_at indexes added for these filters.
        today_start = timezone.localtime().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_end = today_start + timedelta(days=1)
        today = today_start.date()
        yesterday_start = today_start - timedelta(days=1)
        week_start = today_start - timedelta(days=6)
        previous_week_start = week_start - timedelta(days=7)
        month_start = today_start - timedelta(days=29)
        previous_month_start = month_start - timedelta(days=30)

        try:
            trend_days = int(self.request.GET.get('range', 14))
        except (TypeError, ValueError):
            trend_days = 14
        trend_days = trend_days if trend_days in {7, 14, 30} else 14
        trend_start_date = today - timedelta(days=trend_days - 1)
        trend_start = today_start - timedelta(days=trend_days - 1)

        downloads_qs = Download.objects.all()
        download_stats = downloads_qs.aggregate(
            total=Count('id'),
            today=Count(
                'id',
                filter=Q(downloaded_at__gte=today_start, downloaded_at__lt=today_end),
            ),
            yesterday=Count(
                'id',
                filter=Q(
                    downloaded_at__gte=yesterday_start, downloaded_at__lt=today_start
                ),
            ),
            week=Count('id', filter=Q(downloaded_at__gte=week_start)),
            previous_week=Count(
                'id',
                filter=Q(
                    downloaded_at__gte=previous_week_start,
                    downloaded_at__lt=week_start,
                ),
            ),
            month=Count('id', filter=Q(downloaded_at__gte=month_start)),
            previous_month=Count(
                'id',
                filter=Q(
                    downloaded_at__gte=previous_month_start,
                    downloaded_at__lt=month_start,
                ),
            ),
            unique_ips=Count('ip_address', distinct=True),
            unique_users=Count('user', distinct=True),
        )
        total_downloads = download_stats['total']
        today_downloads = download_stats['today']
        yesterday_downloads = download_stats['yesterday']
        week_downloads = download_stats['week']
        previous_week_downloads = download_stats['previous_week']
        month_downloads = download_stats['month']
        previous_month_downloads = download_stats['previous_month']
        unique_downloaders = download_stats['unique_ips']
        registered_downloaders = download_stats['unique_users']

        # Application counters are kept for older installs; recorded Download
        # rows are the source of truth for time-based analytics.
        apps = list(
            DesktopApplication.objects.annotate(
                recorded_downloads=Count('downloads')
            )
        )
        app_counter_total = sum(app.download_count for app in apps)
        app_stats = []
        for app in apps:
            downloads = app.recorded_downloads or app.download_count
            app_stats.append({
                'pk': app.pk,
                'name': app.name,
                'logo': app.logo,
                'platform_key': app.platform,
                'platform': app.get_platform_display(),
                'published': app.published,
                'downloads': downloads,
                'recorded_downloads': app.recorded_downloads,
                'counter_downloads': app.download_count,
            })
        app_download_total = sum(item['downloads'] for item in app_stats)
        for item in app_stats:
            item['share'] = round(
                (item['downloads'] / app_download_total) * 100, 1
            ) if app_download_total else 0.0
        app_stats.sort(key=lambda item: (-item['downloads'], item['name'].lower()))

        platform_totals = defaultdict(int)
        for item in app_stats:
            platform_totals[item['platform_key']] += item['downloads']
        platform_labels = dict(DesktopApplication.PLATFORM_CHOICES)
        platform_data = [
            {
                'key': key,
                'label': platform_labels.get(key, key.replace('_', ' ').title()),
                'count': count,
                'share': round((count / app_download_total) * 100, 1)
                if app_download_total else 0.0,
            }
            for key, count in platform_totals.items()
            if count > 0
        ]
        platform_data.sort(key=lambda item: (-item['count'], item['label']))

        daily_counts = defaultdict(int)
        for row in (
            downloads_qs.filter(downloaded_at__gte=trend_start)
            .annotate(day=TruncDate('downloaded_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        ):
            daily_counts[row['day']] += row['count']
        trend_data = []
        for offset in range(trend_days):
            day = trend_start_date + timedelta(days=offset)
            trend_data.append({
                'date': day.isoformat(),
                'label': day.strftime('%b %d'),
                'count': daily_counts.get(day, 0),
            })

        recent_downloads = list(
            downloads_qs.select_related('application', 'version', 'user')[:8]
        )

        # Content, audience and engagement metrics from the rest of the site.
        published_posts_qs = BlogPost.objects.filter(status='published')
        blog_stats = published_posts_qs.aggregate(
            posts=Count('id'), views=Sum('views_count')
        )
        published_posts = blog_stats['posts']
        total_blog_views = blog_stats['views'] or 0

        comment_stats = Comment.objects.aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(is_approved=True)),
            pending=Count('id', filter=Q(is_approved=False)),
        )
        total_comments = comment_stats['total']
        approved_comments = comment_stats['approved']
        pending_comments = comment_stats['pending']
        total_likes = PostLike.objects.count()

        subscriber_stats = NewsletterSubscriber.objects.aggregate(
            active=Count('id', filter=Q(is_active=True)),
            recent=Count('id', filter=Q(created_at__gte=month_start)),
        )
        active_subscribers = subscriber_stats['active']
        new_subscribers_30d = subscriber_stats['recent']

        message_stats = ContactMessage.objects.aggregate(
            total=Count('id'),
            unread=Count('id', filter=Q(status='unread')),
            recent=Count('id', filter=Q(created_at__gte=month_start)),
        )
        total_messages = message_stats['total']
        unread_messages = message_stats['unread']
        messages_30d = message_stats['recent']

        top_posts = list(
            published_posts_qs.annotate(
                analytics_comments=Count(
                    'comments', filter=Q(comments__is_approved=True), distinct=True
                ),
                analytics_likes=Count('likes', distinct=True),
            ).order_by('-views_count', '-published_at')[:5]
        )

        activity = []
        for download in recent_downloads:
            activity.append(_activity_item(
                'download', 'fas fa-download',
                download.application.name,
                'New tracked download',
                download.downloaded_at,
                reverse('dashboard:app_detail', args=[download.application_id]),
                'accent',
            ))
        for message in ContactMessage.objects.all()[:5]:
            activity.append(_activity_item(
                'message', 'fas fa-envelope',
                message.name, message.subject, message.created_at,
                reverse('dashboard:message_detail', args=[message.pk]),
                'cyan',
            ))
        for subscriber in NewsletterSubscriber.objects.all()[:5]:
            activity.append(_activity_item(
                'subscriber', 'fas fa-user-plus',
                subscriber.name or subscriber.email,
                'New newsletter subscriber', subscriber.created_at,
                reverse('dashboard:subscriber_list'),
                'green',
            ))
        for post in published_posts_qs.order_by('-published_at', '-created_at')[:5]:
            activity.append(_activity_item(
                'post', 'fas fa-newspaper',
                post.title, 'Published article',
                post.published_at or post.created_at,
                reverse('dashboard:blog_edit', args=[post.pk]),
                'amber',
            ))
        activity.sort(key=lambda item: item['timestamp'], reverse=True)

        context.update({
            'total_downloads': total_downloads,
            'app_counter_total': app_counter_total,
            'today_downloads': today_downloads,
            'today_change': _percent_change(today_downloads, yesterday_downloads),
            'week_downloads': week_downloads,
            'week_change': _percent_change(week_downloads, previous_week_downloads),
            'month_downloads': month_downloads,
            'month_change': _percent_change(month_downloads, previous_month_downloads),
            'unique_downloaders': unique_downloaders,
            'registered_downloaders': registered_downloaders,
            'app_download_stats': app_stats,
            'app_download_total': app_download_total,
            'total_apps': len(apps),
            'published_apps': sum(1 for app in apps if app.published),
            'most_downloaded': next(
                (item for item in app_stats if item['downloads'] > 0), None
            ),
            'recent_downloads': recent_downloads[:6],
            'trend_data': trend_data,
            'trend_days': trend_days,
            'trend_range_choices': [7, 14, 30],
            'platform_data': platform_data,
            'published_posts': published_posts,
            'total_blog_views': total_blog_views,
            'total_comments': total_comments,
            'approved_comments': approved_comments,
            'pending_comments': pending_comments,
            'total_likes': total_likes,
            'active_subscribers': active_subscribers,
            'new_subscribers_30d': new_subscribers_30d,
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'messages_30d': messages_30d,
            'content_counts': {
                'desktop_apps': sum(1 for app in apps if app.published),
                'web_projects': WebProject.objects.count(),
                'mobile_apps': MobileApp.objects.count(),
                'graphic_designs': GraphicDesignProject.objects.filter(published=True).count(),
            },
            'top_posts': top_posts,
            'recent_activity': activity[:8],
        })
        return context


class SiteSettingsView(DashboardLoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = SiteSettingsForm
    template_name = 'dashboard/site_settings.html'
    success_url = reverse_lazy('dashboard:site_settings')
    success_message = 'Site settings updated successfully.'

    def get_object(self, queryset=None):
        from apps.core.models import SiteSettings
        return SiteSettings.load()


class CommentListView(DashboardLoginRequiredMixin, ListView):
    model = Comment
    template_name = 'dashboard/comment_list.html'
    context_object_name = 'comments'
    paginate_by = 20

    def get_queryset(self):
        qs = Comment.objects.select_related('post__category', 'post__author').all()
        status = self.request.GET.get('status')
        post_id = self.request.GET.get('post_id')
        search = self.request.GET.get('q')

        if status == 'approved':
            qs = qs.filter(is_approved=True)
        elif status == 'pending':
            qs = qs.filter(is_approved=False)

        if post_id:
            qs = qs.filter(post_id=post_id)

        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(body__icontains=search) |
                Q(post__title__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comment_stats = Comment.objects.aggregate(
            total=Count('id'),
            approved=Count('id', filter=Q(is_approved=True)),
            pending=Count('id', filter=Q(is_approved=False)),
        )
        context['total_comments'] = comment_stats['total']
        context['approved_comments'] = comment_stats['approved']
        context['pending_comments'] = comment_stats['pending']
        context['current_status'] = self.request.GET.get('status', '')
        context['current_post_id'] = self.request.GET.get('post_id', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['posts'] = BlogPost.objects.only('id', 'title').order_by('title')
        return context


class CommentToggleApprovalView(DashboardLoginRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        comment.is_approved = not comment.is_approved
        comment.save(update_fields=['is_approved'])

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'is_approved': comment.is_approved,
                'message': f"Comment by {comment.name} is now {'approved' if comment.is_approved else 'hidden'}."
            })

        status_str = 'approved' if comment.is_approved else 'hidden'
        messages.success(request, f"Comment has been {status_str}.")
        return redirect('dashboard:comment_list')


class CommentDeleteView(DashboardLoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'dashboard/comment_confirm_delete.html'
    context_object_name = 'comment'
    success_url = reverse_lazy('dashboard:comment_list')
    success_message = 'Comment was deleted successfully.'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)
