from django.db import models
from employees.models import Employee


class Payroll(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('paid', 'Paid')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    month = models.IntegerField()
    year = models.IntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    generated_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        self.net_salary = Decimal(str(self.basic_salary or 0)) + Decimal(str(self.allowances or 0)) - Decimal(str(self.deductions or 0))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.name} - {self.month}/{self.year}"

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']
