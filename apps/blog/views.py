from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import BlogPost, BlogCategory, Tag, Comment, PostLike
from .forms import CommentForm


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
        context['comment_form'] = CommentForm()
        context['has_liked'] = self.object.is_liked_by(self.request)
        context['likes_count'] = self.object.likes_count
        context['related_posts'] = BlogPost.objects.filter(
            status='published', category=self.object.category
        ).exclude(pk=self.object.pk)[:3]
        context['recent_articles'] = BlogPost.objects.filter(
            status='published', is_recent=True
        ).exclude(pk=self.object.pk).select_related('category').order_by('-published_at', '-created_at')[:5]
        context['trending_articles'] = BlogPost.objects.filter(
            status='published', is_trending=True
        ).exclude(pk=self.object.pk).select_related('category').order_by('-views_count', '-published_at', '-created_at')[:5]
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj


class BlogPostCommentCreateView(View):
    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status='published')
        form = CommentForm(request.POST)
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1' or 'application/json' in request.headers.get('Accept', '')

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.ip_address = request.META.get('REMOTE_ADDR')
            comment.is_approved = True
            comment.save()

            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': 'Your comment has been posted successfully!',
                    'comment': {
                        'id': comment.pk,
                        'name': comment.name,
                        'initial': comment.name[0].upper(),
                        'body': comment.body,
                        'created_at': comment.created_at.strftime('%b %d, %Y at %I:%M %p'),
                        'date_short': comment.created_at.strftime('%b %d, %Y'),
                        'time_short': comment.created_at.strftime('%I:%M %p'),
                    },
                    'comments_count': post.approved_comments_count
                })

            messages.success(request, 'Your comment has been posted successfully!')
            return redirect(f"{post.get_absolute_url()}#comments-section")

        if is_ajax:
            error_list = []
            for field, errors in form.errors.items():
                for err in errors:
                    error_list.append(f"{field.capitalize()}: {err}" if field != '__all__' else err)
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
                'message': error_list[0] if error_list else 'Please correct the errors in the form.'
            }, status=400)

        messages.error(request, 'There was a problem submitting your comment. Please check the fields.')
        return redirect(f"{post.get_absolute_url()}#comment-form")


class BlogPostLikeToggleView(View):
    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status='published')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1' or 'application/json' in request.headers.get('Accept', '')

        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        ip = request.META.get('REMOTE_ADDR')

        if request.user.is_authenticated:
            existing_like = PostLike.objects.filter(post=post, user=request.user).first()
        else:
            existing_like = PostLike.objects.filter(post=post, session_key=session_key).first()

        if existing_like:
            existing_like.delete()
            liked = False
            msg = 'You unliked this article.'
        else:
            PostLike.objects.create(
                post=post,
                user=request.user if request.user.is_authenticated else None,
                session_key=session_key,
                ip_address=ip
            )
            liked = True
            msg = 'Thank you for liking this article!'

        likes_count = post.likes_count

        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'liked': liked,
                'likes_count': likes_count,
                'message': msg
            })

        messages.info(request, msg)
        return redirect(f"{post.get_absolute_url()}#like-section")


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
