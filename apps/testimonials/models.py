from django.db import models


class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    company = models.CharField(max_length=200, blank=True)
    position = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='uploads/testimonials/', blank=True, null=True)
    review = models.TextField()
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'

    def __str__(self):
        return f"{self.client_name} - {self.company}"
