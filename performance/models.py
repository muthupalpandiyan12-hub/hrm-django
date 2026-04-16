from django.db import models
from employees.models import Employee
from django.contrib.auth.models import User


class PerformanceReview(models.Model):
    PERIOD_CHOICES = [
        ('Q1', 'Q1 (Jan-Mar)'),
        ('Q2', 'Q2 (Apr-Jun)'),
        ('Q3', 'Q3 (Jul-Sep)'),
        ('Q4', 'Q4 (Oct-Dec)'),
        ('annual', 'Annual'),
    ]
    RATING_CHOICES = [
        (1, 'Poor'),
        (2, 'Below Average'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reviews')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    year = models.IntegerField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-created_at']
        unique_together = ['employee', 'period', 'year']

    def __str__(self):
        return f"{self.employee.name} — {self.get_period_display()} {self.year}"
