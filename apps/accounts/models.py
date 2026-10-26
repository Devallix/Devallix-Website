from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    job_title = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.get_full_name() or self.username

    def get_absolute_url(self):
        return reverse('accounts:profile')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    about = models.TextField(blank=True)
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    philosophy = models.TextField(blank=True)
    years_experience = models.PositiveIntegerField(default=0)
    projects_completed = models.PositiveIntegerField(default=0)
    happy_clients = models.PositiveIntegerField(default=0)
    coffee_cups = models.PositiveIntegerField(default=0)
    resume = models.FileField(upload_to='uploads/resumes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_absolute_url(self):
        return reverse('accounts:profile')


class TimelineEvent(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='timeline_events')
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('education', 'Education'),
            ('work', 'Work Experience'),
            ('certification', 'Certification'),
            ('achievement', 'Achievement'),
        ],
        default='work'
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Timeline Event'
        verbose_name_plural = 'Timeline Events'

    def __str__(self):
        return f"{self.title} at {self.organization}"
