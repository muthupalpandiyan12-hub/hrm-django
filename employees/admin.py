from django.contrib import admin
from .models import Employee, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'name', 'email', 'department', 'position', 'salary', 'status']
    list_filter = ['status', 'department', 'gender']
    search_fields = ['name', 'email', 'employee_id']
    list_per_page = 20
