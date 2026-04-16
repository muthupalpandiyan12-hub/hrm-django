from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'employee', 'department']
    list_filter  = ['role']
    search_fields = ['user__username', 'employee__name']
