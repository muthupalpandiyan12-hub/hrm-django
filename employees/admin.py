from django.contrib import admin
from .models import Employee, Department, SalaryHistory


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'email', 'position', 'status')
    list_filter = ('status', 'gender')
    search_fields = ('name', 'email', 'employee_id')
    readonly_fields = ('date_joined',)

    fieldsets = (
        ('Basic Information', {
            'fields': ('employee_id', 'name', 'email', 'phone')
        }),
        ('Personal Details', {
            'fields': ('gender', 'date_of_birth', 'address'),
            'classes': ('collapse',)
        }),
        ('Employment', {
            'fields': ('department', 'position', 'salary', 'status', 'date_joined')
        }),
    )


class SalaryHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'old_salary', 'new_salary', 'effective_date', 'reason_type')
    list_filter = ('reason_type', 'effective_date')
    search_fields = ('employee__name',)
    readonly_fields = ('created_at',)


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(SalaryHistory, SalaryHistoryAdmin)
