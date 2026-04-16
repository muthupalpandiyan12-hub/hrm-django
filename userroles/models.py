from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee, Department


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin',    'Admin / HR Manager'),
        ('manager',  'Manager'),
        ('employee', 'Employee'),
    ]

    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    employee   = models.OneToOneField(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role == 'manager'

    def is_employee(self):
        return self.role == 'employee'

    def __str__(self):
        return f"{self.user.username} ({self.role})"
