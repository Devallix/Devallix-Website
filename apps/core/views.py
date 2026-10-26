from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404
from django.views.decorators.cache import cache_control
from django.views.generic import TemplateView

from apps.core.models import SiteSettings
from apps.desktop_apps.models import DesktopApplication
from apps.web_projects.models import WebProject
from apps.mobile_apps.models import MobileApp
from apps.testimonials.models import Testimonial
from apps.portfolio.models import Skill, SkillCategory

FAVICON_MIME_TYPES = {
    '.ico': 'image/x-icon',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
    '.gif': 'image/gif',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
}


@cache_control(public=True, max_age=60 * 60 * 24)
def favicon(request):
    """Serve the uploaded favicon, falling back to the bundled icon.

    This uses a stable URL instead of a /media/ URL so the icon still works
    when media files are not served directly by the web server.
    """
    site = SiteSettings.load()

    if site.favicon:
        try:
            path = Path(site.favicon.path)
        except (ValueError, OSError):
            path = None
        if path and path.is_file():
            content_type = FAVICON_MIME_TYPES.get(
                path.suffix.lower(), 'image/x-icon'
            )
            return FileResponse(open(path, 'rb'), content_type=content_type)

    fallback = finders.find('images/favicon.ico')
    if fallback:
        return FileResponse(open(fallback, 'rb'), content_type='image/x-icon')

    collected = Path(settings.STATIC_ROOT) / 'images' / 'favicon.ico'
    if collected.is_file():
        return FileResponse(open(collected, 'rb'), content_type='image/x-icon')

    raise Http404('Favicon not found')


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_apps'] = DesktopApplication.objects.filter(
            featured=True, published=True
        )[:6]
        context['latest_apps'] = DesktopApplication.objects.filter(
            published=True
        ).order_by('-created_at')[:6]
        context['featured_projects'] = WebProject.objects.filter(
            featured=True
        )[:6]
        context['latest_projects'] = WebProject.objects.filter(
            status='completed'
        ).order_by('-created_at')[:6]
        context['featured_mobile_apps'] = MobileApp.objects.filter(
            featured=True, status='completed'
        )[:6]
        context['testimonials'] = Testimonial.objects.filter(
            featured=True, is_active=True
        )[:5]
        context['skills'] = Skill.objects.filter(is_featured=True)[:12]
        context['skill_categories'] = SkillCategory.objects.all()
        context['stats'] = {
            'apps_built': DesktopApplication.objects.filter(published=True).count(),
            'web_projects': WebProject.objects.filter(status='completed').count(),
            'total_downloads': sum(
                app.download_count for app in DesktopApplication.objects.filter(published=True)
            ),
        }
        return context


class AboutView(TemplateView):
    template_name = 'core/about.html'


class SkillsView(TemplateView):
    template_name = 'core/skills.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SkillCategory.objects.prefetch_related('skills').all()
        context['skills'] = Skill.objects.select_related('category').all()
        return context


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'


class TermsView(TemplateView):
    template_name = 'core/terms.html'
