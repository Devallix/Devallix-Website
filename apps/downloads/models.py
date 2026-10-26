from django.db import models
from django.conf import settings


class Download(models.Model):
    application = models.ForeignKey('desktop_apps.DesktopApplication', on_delete=models.CASCADE, related_name='downloads')
    version = models.ForeignKey('desktop_apps.ApplicationVersion', on_delete=models.SET_NULL, null=True, blank=True, related_name='downloads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = 'Download'
        verbose_name_plural = 'Downloads'

    def __str__(self):
        return f"Download: {self.application.name} by {self.user or self.ip_address}"
