from django.contrib import admin
from .models import LeaveType, LeaveRequest


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'max_days']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'applied_on']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__name', 'employee__employee_id']
    list_per_page = 20
