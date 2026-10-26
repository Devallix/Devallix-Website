from django.views.generic import ListView, DetailView
from .models import MobileApp


class MobileAppListView(ListView):
    model = MobileApp
    template_name = 'mobile_apps/app_list.html'
    context_object_name = 'apps'
    paginate_by = 12

    def get_queryset(self):
        qs = MobileApp.objects.filter(status='completed')
        platform = self.request.GET.get('platform')
        search = self.request.GET.get('q')
        sort = self.request.GET.get('sort', '-created_at')

        if platform:
            qs = qs.filter(platform=platform)
        if search:
            qs = qs.filter(name__icontains=search)

        valid_sort = ['-created_at', 'created_at', 'name', '-display_order']
        if sort in valid_sort:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_platform'] = self.request.GET.get('platform', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['total_count'] = self.get_queryset().count()
        return context


class MobileAppDetailView(DetailView):
    model = MobileApp
    template_name = 'mobile_apps/app_detail.html'
    context_object_name = 'app'

    def get_queryset(self):
        return MobileApp.objects.filter(status='completed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_apps'] = MobileApp.objects.filter(
            status='completed'
        ).exclude(pk=self.object.pk)[:3]
        return context
