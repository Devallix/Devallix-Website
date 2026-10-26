from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import BlogPost, BlogCategory, Tag


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        qs = BlogPost.objects.filter(status='published')
        category = self.request.GET.get('category')
        tag = self.request.GET.get('tag')
        search = self.request.GET.get('q')

        if category:
            qs = qs.filter(category__slug=category)
        if tag:
            qs = qs.filter(tags__slug=tag)
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(content__icontains=search)

        return qs.select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.all()
        context['tags'] = Tag.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_tag'] = self.request.GET.get('tag', '')
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        context['related_posts'] = BlogPost.objects.filter(
            status='published', category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


class BlogCategoryDetailView(ListView):
    model = BlogPost
    template_name = 'blog/category_detail.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            status='published', category=self.category
        ).select_related('author').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = BlogCategory.objects.all()
        return context


class BlogTagDetailView(ListView):
    model = BlogPost
    template_name = 'blog/tag_detail.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            status='published', tags=self.tag
        ).select_related('author', 'category').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['tags'] = Tag.objects.all()
        return context
