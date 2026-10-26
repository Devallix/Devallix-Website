from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class WebProject(models.Model):
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=300)
    description = models.TextField()
    technologies = models.ManyToManyField('portfolio.Technology', blank=True, related_name='web_projects')
    image = models.ImageField(upload_to='uploads/web_projects/', blank=True, null=True)
    live_demo_url = models.URLField(blank=True)
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
        verbose_name = 'Web Project'
        verbose_name_plural = 'Web Projects'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('web_projects:project_detail', kwargs={'slug': self.slug})


class ProjectImage(models.Model):
    project = models.ForeignKey(WebProject, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='uploads/web_projects/images/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Project Image'
        verbose_name_plural = 'Project Images'

    def __str__(self):
        return f"Image for {self.project.name}"
