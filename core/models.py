from django.db import models
from django.contrib.auth.models import User


class Holiday(models.Model):
    TYPE_CHOICES = [
        ('public', 'Public Holiday'),
        ('company', 'Company Holiday'),
        ('optional', 'Optional Holiday'),
    ]
    name = models.CharField(max_length=100)
    date = models.DateField()
    holiday_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='public')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_active = models.BooleanField(default=True)
    expires_on = models.DateField(null=True, blank=True)
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
