from apps.core.models import SiteSettings


def site_settings_context(request):
    try:
        settings = SiteSettings.load()
    except Exception:
        settings = None
    return {'site_settings': settings}
