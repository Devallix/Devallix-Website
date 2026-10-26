from django.db import models


class Technology(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True, help_text='Font Awesome icon class')
    color = models.CharField(max_length=7, default='#B6FF00')
    website = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Technology'
        verbose_name_plural = 'Technologies'

    def __str__(self):
        return self.name


class SkillCategory(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']
        verbose_name = 'Skill Category'
        verbose_name_plural = 'Skill Categories'

    def __str__(self):
        return self.name


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('languages', 'Programming Languages'),
        ('frameworks', 'Frameworks'),
        ('desktop', 'Desktop Development'),
        ('web', 'Web Development'),
        ('databases', 'Databases'),
        ('tools', 'Development Tools'),
    ]

    LEVEL_CHOICES = [
        (90, 'Expert'),
        (75, 'Advanced'),
        (60, 'Intermediate'),
        (40, 'Beginner'),
    ]

    name = models.CharField(max_length=100)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills', null=True, blank=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='languages')
    proficiency_level = models.PositiveIntegerField(default=75, choices=LEVEL_CHOICES)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name
