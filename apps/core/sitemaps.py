from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import BlogPost
from apps.desktop_apps.models import DesktopApplication
from apps.graphic_design.models import GraphicDesignProject
from apps.mobile_apps.models import MobileApp
from apps.web_projects.models import WebProject


class CanonicalDomainSitemap(Sitemap):
    """Always emit the canonical site domain, regardless of request host."""

    protocol = 'https'

    def get_domain(self, site=None):
        return settings.SITE_DOMAIN


class StaticViewSitemap(CanonicalDomainSitemap):
    """Public pages that are always available."""

    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return [
            'core:home',
            'core:about',
            'core:skills',
            'portfolio:portfolio',
            'desktop_apps:app_list',
            'web_projects:project_list',
            'mobile_apps:app_list',
            'graphic_design:design_list',
            'blog:post_list',
            'testimonials:testimonial_list',
            'contact:contact',
            'core:privacy_policy',
            'core:terms',
        ]

    def location(self, item):
        return reverse(item)


class BlogPostSitemap(CanonicalDomainSitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at


class WebProjectSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return WebProject.objects.exclude(status='archived')

    def lastmod(self, obj):
        return obj.updated_at


class DesktopApplicationSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return DesktopApplication.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at


class MobileAppSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return MobileApp.objects.filter(status='completed')

    def lastmod(self, obj):
        return obj.updated_at


class GraphicDesignSitemap(CanonicalDomainSitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return GraphicDesignProject.objects.filter(published=True)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    'static': StaticViewSitemap,
    'blog': BlogPostSitemap,
    'web-projects': WebProjectSitemap,
    'desktop-apps': DesktopApplicationSitemap,
    'mobile-apps': MobileAppSitemap,
    'graphic-design': GraphicDesignSitemap,
}
