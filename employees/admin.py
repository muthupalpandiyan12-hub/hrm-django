from django.contrib import admin
from .models import Employee, Department, SalaryHistory

# Register models with default admin - no customization
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(SalaryHistory)
