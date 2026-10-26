from django.views.generic import TemplateView
from apps.desktop_apps.models import DesktopApplication
from apps.web_projects.models import WebProject
from apps.mobile_apps.models import MobileApp
from apps.testimonials.models import Testimonial
from apps.portfolio.models import Skill, SkillCategory


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
