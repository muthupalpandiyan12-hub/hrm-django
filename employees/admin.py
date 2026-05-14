from django.contrib import admin
from .models import Employee, Department, SalaryHistory


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'email', 'position', 'status')
    list_filter = ('status', 'gender')
    search_fields = ('name', 'email', 'employee_id')


@admin.register(SalaryHistory)
class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'old_salary', 'new_salary', 'effective_date')
    search_fields = ('employee__name',)
