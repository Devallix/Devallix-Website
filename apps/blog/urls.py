from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='post_list'),
    path('useful-website-directory/', views.DirectoryView.as_view(), name='useful_website_directory'),
    path('useful-website-directory/<slug:slug>/', views.DirectorySubCategoryView.as_view(), name='useful_website_directory_subcategory'),
    path('category/<slug:slug>/', views.BlogCategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.BlogTagDetailView.as_view(), name='tag_detail'),
    path('<slug:category_slug>/<slug:slug>/comment/', views.BlogPostCommentCreateView.as_view(), name='post_comment'),
    path('<slug:category_slug>/<slug:slug>/like/', views.BlogPostLikeToggleView.as_view(), name='post_like_toggle'),
    path('<slug:category_slug>/<slug:slug>/', views.BlogPostDetailView.as_view(), name='post_detail'),
    path('<slug:slug>/comment/', views.BlogPostCommentCreateView.as_view(), name='post_comment_plain'),
    path('<slug:slug>/like/', views.BlogPostLikeToggleView.as_view(), name='post_like_toggle_plain'),
    path('<slug:slug>/', views.BlogPostDetailView.as_view(), name='post_detail_plain'),
]
