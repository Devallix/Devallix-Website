from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class MobileApp(models.Model):
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('cross_platform', 'Cross Platform'),
    ]

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='cross_platform')
    technologies = models.ManyToManyField('portfolio.Technology', blank=True, related_name='mobile_apps')
    version = models.CharField(max_length=50, default='1.0.0')
    logo = models.ImageField(upload_to='uploads/mobile_apps/logos/', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/mobile_apps/', blank=True, null=True)
    play_store_url = models.URLField(blank=True)
    app_store_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Mobile Application'
        verbose_name_plural = 'Mobile Applications'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('mobile_apps:app_detail', kwargs={'slug': self.slug})
