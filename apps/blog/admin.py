from django.contrib import admin
from .models import BlogPost, BlogCategory, Tag, Comment, PostLike


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('name', 'body', 'is_approved', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'post', 'is_approved', 'created_at', 'ip_address')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'body', 'post__title')
    actions = ['approve_comments', 'unapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_comments.short_description = "Unapprove selected comments"


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'session_key', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'user__username', 'session_key', 'ip_address')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'published_at')
    list_filter = ('status', 'featured', 'is_recent', 'is_trending', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CommentInline]


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
