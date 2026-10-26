from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('unread', 'Unread'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unread')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject}"

    def mark_read(self):
        self.status = 'read'
        self.save(update_fields=['status'])

    def mark_replied(self):
        self.status = 'replied'
        self.save(update_fields=['status'])

    def archive(self):
        self.status = 'archived'
        self.save(update_fields=['status'])
