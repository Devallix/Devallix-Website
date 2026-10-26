from django.views.generic import TemplateView
from .models import Skill, SkillCategory, Technology


class PortfolioView(TemplateView):
    template_name = 'portfolio/portfolio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = SkillCategory.objects.prefetch_related('skills').all()
        context['skills'] = Skill.objects.select_related('category').all()
        context['technologies'] = Technology.objects.all()
        context['desktop_apps'] = 'desktop_apps'
        context['web_projects'] = 'web_projects'
        return context
