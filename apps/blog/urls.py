from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='post_list'),
    path('category/<slug:slug>/', views.BlogCategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:slug>/', views.BlogTagDetailView.as_view(), name='tag_detail'),
    path('<slug:slug>/comment/', views.BlogPostCommentCreateView.as_view(), name='post_comment'),
    path('<slug:slug>/like/', views.BlogPostLikeToggleView.as_view(), name='post_like_toggle'),
    path('<slug:slug>/', views.BlogPostDetailView.as_view(), name='post_detail'),
]
