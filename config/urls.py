from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('portfolio/', include('apps.portfolio.urls')),
    path('desktop-apps/', include('apps.desktop_apps.urls')),
    path('web-apps/', include('apps.web_projects.urls')),
    path('mobile-apps/', include('apps.mobile_apps.urls')),
    path('graphic-design/', include('apps.graphic_design.urls')),
    path('blog/', include('apps.blog.urls')),
    path('contact/', include('apps.contact.urls')),
    path('testimonials/', include('apps.testimonials.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
