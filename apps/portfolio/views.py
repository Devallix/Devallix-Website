from django.views.generic import TemplateView

from apps.desktop_apps.models import DesktopApplication
from apps.graphic_design.models import GraphicDesignProject
from apps.mobile_apps.models import MobileApp
from apps.web_projects.models import WebProject

from .models import Skill, SkillCategory, Technology


class PortfolioView(TemplateView):
    template_name = 'portfolio/portfolio.html'

    @staticmethod
    def _build_item(*, title, description, url, image, type_label, icon,
                    techs, meta, accent, accent_soft, created):
        return {
            'title': title,
            'description': description,
            'url': url,
            'image': image,
            'type_label': type_label,
            'icon': icon,
            'techs': [tech for tech in techs if tech],
            'meta': meta,
            'accent': accent,
            'accent_soft': accent_soft,
            'created': created,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        desktop_apps = DesktopApplication.objects.filter(published=True)
        web_projects = WebProject.objects.all()
        mobile_apps = MobileApp.objects.all()
        designs = GraphicDesignProject.objects.filter(published=True)

        context['counts'] = {
            'desktop': desktop_apps.count(),
            'web': web_projects.count(),
            'mobile': mobile_apps.count(),
            'design': designs.count(),
        }
        context['total_projects'] = sum(context['counts'].values())

        items = []

        for app in desktop_apps.select_related('category').order_by('-featured', '-created_at')[:2]:
            items.append(self._build_item(
                title=app.name,
                description=app.short_description,
                url=app.get_absolute_url(),
                image=app.banner or app.logo,
                type_label='Desktop App',
                icon='fas fa-desktop',
                techs=[app.get_platform_display(), app.get_license_type_display()],
                meta=f'v{app.version} · {app.download_count:,} downloads',
                accent='#B6FF00',
                accent_soft='rgba(182, 255, 0, 0.18)',
                created=app.created_at,
            ))

        for project in web_projects.prefetch_related('technologies').order_by('-featured', 'display_order', '-created_at')[:2]:
            items.append(self._build_item(
                title=project.name,
                description=project.short_description,
                url=project.get_absolute_url(),
                image=project.image,
                type_label='Web App',
                icon='fas fa-globe',
                techs=list(project.technologies.values_list('name', flat=True)[:3]),
                meta=project.get_status_display(),
                accent='#00D9FF',
                accent_soft='rgba(0, 217, 255, 0.18)',
                created=project.created_at,
            ))

        for app in mobile_apps.prefetch_related('technologies').order_by('-featured', 'display_order', '-created_at')[:1]:
            items.append(self._build_item(
                title=app.name,
                description=app.short_description,
                url=app.get_absolute_url(),
                image=app.image or app.logo,
                type_label='Mobile App',
                icon='fas fa-mobile-alt',
                techs=[app.get_platform_display()] + list(app.technologies.values_list('name', flat=True)[:2]),
                meta=f'v{app.version}',
                accent='#B98BFF',
                accent_soft='rgba(185, 139, 255, 0.18)',
                created=app.created_at,
            ))

        for design in designs.order_by('-featured', 'display_order', '-created_at')[:1]:
            items.append(self._build_item(
                title=design.name,
                description=design.short_description,
                url=design.get_absolute_url(),
                image=design.image,
                type_label='Graphic Design',
                icon='fas fa-palette',
                techs=[tool.strip() for tool in design.tools.split(',')[:3] if tool.strip()],
                meta=design.get_category_display(),
                accent='#FF8A8A',
                accent_soft='rgba(255, 138, 138, 0.18)',
                created=design.created_at,
            ))

        items.sort(key=lambda item: item['created'], reverse=True)
        context['featured_items'] = items[:6]

        context['categories'] = SkillCategory.objects.prefetch_related('skills').all()
        context['skills'] = Skill.objects.select_related('category').all()
        context['technologies'] = Technology.objects.all()
        return context
