from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class GraphicDesignProject(models.Model):
    CATEGORY_CHOICES = [
        ('logo', 'Logo Design'),
        ('branding', 'Branding'),
        ('ui_ux', 'UI/UX Design'),
        ('social_media', 'Social Media'),
        ('print', 'Print Design'),
        ('illustration', 'Illustration'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    image = models.ImageField(upload_to='uploads/graphic_design/', blank=True, null=True)
    client = models.CharField(max_length=200, blank=True)
    tools = models.CharField(max_length=300, blank=True, help_text='Comma separated list of tools used')
    project_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Graphic Design Project'
        verbose_name_plural = 'Graphic Design Projects'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('graphic_design:design_detail', kwargs={'slug': self.slug})
