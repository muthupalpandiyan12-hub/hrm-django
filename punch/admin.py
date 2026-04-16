from django.contrib import admin
from .models import WorkSession


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display  = ('employee', 'date', 'punch_in', 'punch_out', 'duration_display', 'is_active')
    list_filter   = ('date', 'employee__department')
    search_fields = ('employee__name', 'employee__employee_id')
    date_hierarchy = 'date'
    ordering      = ('-date', 'punch_in')
