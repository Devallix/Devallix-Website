from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import BlogPost
from apps.desktop_apps.models import DesktopApplication
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
            ('core:home', None),
            ('core:home', 'devallix.com'),
            ('core:about', None),
            ('core:skills', None),
            ('portfolio:portfolio', None),
            ('desktop_apps:app_list', None),
            ('web_projects:project_list', None),
            ('mobile_apps:app_list', None),
            ('graphic_design:design_list', None),
            ('blog:post_list', None),
            ('testimonials:testimonial_list', None),
            ('contact:contact', None),
            ('core:privacy_policy', None),
            ('core:terms', None),
        ]

    def _urls(self, page, site, protocol):
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

        items = self.items()
        paginator = Paginator(items, self.limit)

        try:
            page = paginator.page(page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        for item in page.object_list:
            if isinstance(item, tuple):
                url_name, domain = item
            else:
                url_name, domain = item, None

            path = reverse(url_name)
            if domain:
                full_url = f'{protocol}://{domain}{path}'
            else:
                default_domain = self.get_domain(site)
                full_url = f'{protocol}://{default_domain}{path}'

            priority = self.priority
            if callable(priority):
                priority = priority(url_name)
            lastmod = self.lastmod(url_name)
            changefreq = self.changefreq
            if callable(changefreq):
                changefreq = changefreq(url_name)

            yield {
                'location': full_url,
                'lastmod': lastmod,
                'changefreq': changefreq,
                'priority': priority,
            }

    def lastmod(self, item):
        return None


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
        return []

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
