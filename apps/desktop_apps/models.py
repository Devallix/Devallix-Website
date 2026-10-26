import os
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class ApplicationCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Application Category'
        verbose_name_plural = 'Application Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('desktop_apps:app_list') + f'?category={self.slug}'


class DesktopApplication(models.Model):
    PLATFORM_CHOICES = [
        ('windows', 'Windows'),
        ('macos', 'macOS'),
        ('linux', 'Linux'),
        ('cross_platform', 'Cross Platform'),
    ]

    LICENSE_CHOICES = [
        ('free', 'Free'),
        ('open_source', 'Open Source'),
        ('freemium', 'Freemium'),
        ('trial', 'Trial'),
        ('paid', 'Paid'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(ApplicationCategory, on_delete=models.SET_NULL, null=True, related_name='applications')
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    version = models.CharField(max_length=50, default='1.0.0')
    developer = models.CharField(max_length=200, blank=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default='windows')
    license_type = models.CharField(max_length=20, choices=LICENSE_CHOICES, default='free')
    file_size = models.CharField(max_length=50, blank=True)
    release_date = models.DateField(blank=True, null=True)
    minimum_requirements = models.TextField(blank=True)
    installation_instructions = models.TextField(blank=True)
    logo = models.ImageField(upload_to='uploads/app_icons/', blank=True, null=True)
    banner = models.ImageField(upload_to='uploads/app_banners/', blank=True, null=True)
    installer_file = models.FileField(upload_to='uploads/installers/', blank=True, null=True)
    zip_file = models.FileField(upload_to='uploads/installers/', blank=True, null=True)
    website_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Desktop Application'
        verbose_name_plural = 'Desktop Applications'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.developer:
            self.developer = 'DevPortfolio'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('desktop_apps:app_detail', kwargs={'slug': self.slug})

    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])


class ApplicationVersion(models.Model):
    application = models.ForeignKey(DesktopApplication, on_delete=models.CASCADE, related_name='versions')
    version_number = models.CharField(max_length=50)
    release_date = models.DateField()
    changes = models.TextField()
    release_notes = models.TextField(blank=True)
    installer_file = models.FileField(upload_to='uploads/installers/versions/', blank=True, null=True)
    zip_file = models.FileField(upload_to='uploads/installers/versions/', blank=True, null=True)
    file_size = models.CharField(max_length=50, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-release_date']
        verbose_name = 'Application Version'
        verbose_name_plural = 'Application Versions'

    def __str__(self):
        return f"{self.application.name} v{self.version_number}"

    def save(self, *args, **kwargs):
        if self.is_current:
            ApplicationVersion.objects.filter(
                application=self.application, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Screenshot(models.Model):
    application = models.ForeignKey(DesktopApplication, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='uploads/screenshots/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Screenshot'
        verbose_name_plural = 'Screenshots'

    def __str__(self):
        return f"Screenshot for {self.application.name} - {self.caption}"


class FaqItem(models.Model):
    application = models.ForeignKey(DesktopApplication, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'FAQ Item'
        verbose_name_plural = 'FAQ Items'

    def __str__(self):
        return self.question
