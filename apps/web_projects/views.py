from django.views.generic import ListView, DetailView
from .models import WebProject
from apps.portfolio.models import Technology


class ProjectListView(ListView):
    model = WebProject
    template_name = 'web_projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        qs = WebProject.objects.filter(status='completed')
        tech = self.request.GET.get('tech')
        search = self.request.GET.get('q')
        sort = self.request.GET.get('sort', '-created_at')

        if tech:
            qs = qs.filter(technologies__slug=tech)
        if search:
            qs = qs.filter(name__icontains=search)

        valid_sort = ['-created_at', 'created_at', 'name', '-display_order']
        if sort in valid_sort:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_tech'] = self.request.GET.get('tech', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['total_count'] = self.get_queryset().count()
        context['technologies'] = Technology.objects.all()
        return context


class ProjectDetailView(DetailView):
    model = WebProject
    template_name = 'web_projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_images'] = self.object.images.all()
        context['related_projects'] = WebProject.objects.filter(
            status='completed'
        ).exclude(pk=self.object.pk)[:3]
        return context
