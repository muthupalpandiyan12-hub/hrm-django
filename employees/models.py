from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('terminated', 'Terminated')]

    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.employee_id} - {self.name}"

    class Meta:
        ordering = ['employee_id']


class SalaryHistory(models.Model):
    REASON_CHOICES = [
        ('appraisal', 'Annual Appraisal'),
        ('promotion', 'Promotion'),
        ('correction', 'Correction'),
        ('joining', 'Joining'),
        ('other', 'Other'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_history')
    old_salary = models.DecimalField(max_digits=10, decimal_places=2)
    new_salary = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    reason_type = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.employee} salary change on {self.effective_date}"
