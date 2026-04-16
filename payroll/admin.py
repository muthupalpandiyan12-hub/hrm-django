from django.contrib import admin
from .models import Payroll


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'status']
    list_filter = ['status', 'year', 'month']
    search_fields = ['employee__name', 'employee__employee_id']
    list_per_page = 20
