from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='DevPortfolio')
    site_tagline = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='uploads/site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='uploads/site/', blank=True, null=True)
    hero_title = models.CharField(max_length=300, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_cta_text = models.CharField(max_length=100, default='View Portfolio')
    hero_cta_url = models.CharField(max_length=300, default='/portfolio/')
    about_image = models.ImageField(upload_to='uploads/site/', blank=True, null=True)
    footer_text = models.TextField(blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.TextField(blank=True)
    og_image = models.ImageField(upload_to='uploads/site/', blank=True, null=True)
    google_analytics_code = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('There can be only one SiteSettings instance')
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
