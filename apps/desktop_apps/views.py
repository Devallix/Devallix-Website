from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.http import FileResponse
from .models import DesktopApplication, ApplicationCategory, ApplicationVersion


class AppListView(ListView):
    model = DesktopApplication
    template_name = 'desktop_apps/app_list.html'
    context_object_name = 'applications'
    paginate_by = 12

    def get_queryset(self):
        qs = DesktopApplication.objects.filter(published=True)
        category = self.request.GET.get('category')
        platform = self.request.GET.get('platform')
        search = self.request.GET.get('q')
        sort = self.request.GET.get('sort', '-created_at')

        if category:
            qs = qs.filter(category__slug=category)
        if platform:
            qs = qs.filter(platform=platform)
        if search:
            qs = qs.filter(name__icontains=search)

        valid_sort = ['-created_at', 'name', '-download_count', 'release_date', '-release_date']
        if sort in valid_sort:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ApplicationCategory.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_platform'] = self.request.GET.get('platform', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['total_count'] = self.get_queryset().count()
        return context


class AppDetailView(DetailView):
    model = DesktopApplication
    template_name = 'desktop_apps/app_detail.html'
    context_object_name = 'app'

    def get_queryset(self):
        return DesktopApplication.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['screenshots'] = self.object.screenshots.all()
        context['versions'] = self.object.versions.all()[:10]
        context['faqs'] = self.object.faqs.all()
        context['related_apps'] = DesktopApplication.objects.filter(
            category=self.object.category, published=True
        ).exclude(pk=self.object.pk)[:4]
        return context


def download_app(request, slug):
    app = get_object_or_404(DesktopApplication, slug=slug, published=True)

    if app.installer_file:
        from apps.downloads.models import Download
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')
        Download.objects.create(
            application=app,
            ip_address=ip,
            user_agent=ua,
            user=request.user if request.user.is_authenticated else None,
        )
        app.increment_download()
        return FileResponse(app.installer_file.open('rb'), as_attachment=True, filename=app.installer_file.name.split('/')[-1])

    return redirect('desktop_apps:app_detail', slug=slug)


class CategoryAppListView(AppListView):
    def get_queryset(self):
        self.category = get_object_or_404(ApplicationCategory, slug=self.kwargs['slug'])
        qs = DesktopApplication.objects.filter(
            published=True, category=self.category
        )
        platform = self.request.GET.get('platform')
        if platform:
            qs = qs.filter(platform=platform)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context
