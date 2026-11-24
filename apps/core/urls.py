from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.decorators.cache import cache_page
from . import views
from .sitemaps import sitemaps

app_name = 'core'

urlpatterns = [
    path('favicon.ico', views.favicon, name='favicon'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path(
        'sitemap.xml',
        cache_page(60 * 60)(sitemap),
        {'sitemaps': sitemaps},
        name='sitemap',
    ),
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('skills/', views.SkillsView.as_view(), name='skills'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsView.as_view(), name='terms'),
]
