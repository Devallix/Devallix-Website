from django.views.generic import ListView, DetailView
from .models import GraphicDesignProject


class DesignListView(ListView):
    model = GraphicDesignProject
    template_name = 'graphic_design/design_list.html'
    context_object_name = 'designs'
    paginate_by = 12

    def get_queryset(self):
        qs = GraphicDesignProject.objects.filter(published=True)
        category = self.request.GET.get('category')
        search = self.request.GET.get('q')
        sort = self.request.GET.get('sort', '-created_at')

        if category:
            qs = qs.filter(category=category)
        if search:
            qs = qs.filter(name__icontains=search)

        valid_sort = ['-created_at', 'created_at', 'name', '-display_order']
        if sort in valid_sort:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        context['total_count'] = self.get_queryset().count()
        context['categories'] = GraphicDesignProject.CATEGORY_CHOICES
        return context


class DesignDetailView(DetailView):
    model = GraphicDesignProject
    template_name = 'graphic_design/design_detail.html'
    context_object_name = 'design'

    def get_queryset(self):
        return GraphicDesignProject.objects.filter(published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_designs'] = GraphicDesignProject.objects.filter(
            published=True
        ).exclude(pk=self.object.pk)[:3]
        return context
