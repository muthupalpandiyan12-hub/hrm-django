from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from employees.models import Employee
from attendance.models import Attendance
from leave.models import LeaveRequest
from payroll.models import Payroll
from userroles.helpers import get_user_role, get_user_employee
import datetime


def _get_upcoming_birthdays(days=30):
    """Return employees with birthdays in the next `days` days (ignores year)."""
    today = datetime.date.today()
    upcoming = []
    employees = Employee.objects.filter(status='active', date_of_birth__isnull=False)
    for emp in employees:
        dob = emp.date_of_birth
        try:
            bday_this_year = dob.replace(year=today.year)
        except ValueError:
            # Feb 29 in non-leap year
            bday_this_year = dob.replace(year=today.year, day=28)
        if bday_this_year < today:
            try:
                bday_this_year = dob.replace(year=today.year + 1)
            except ValueError:
                bday_this_year = dob.replace(year=today.year + 1, day=28)
        delta = (bday_this_year - today).days
        if 0 <= delta <= days:
            upcoming.append({'employee': emp, 'days_until': delta, 'date': bday_this_year})
    return sorted(upcoming, key=lambda x: x['days_until'])


def _get_upcoming_anniversaries(days=30):
    """Return employees with work anniversaries in the next `days` days."""
    today = datetime.date.today()
    upcoming = []
    employees = Employee.objects.filter(status='active', date_joined__isnull=False)
    for emp in employees:
        dj = emp.date_joined
        if dj.year == today.year and dj.month == today.month and dj.day == today.day:
            years = 0
        else:
            try:
                ann_this_year = dj.replace(year=today.year)
            except ValueError:
                ann_this_year = dj.replace(year=today.year, day=28)
            if ann_this_year < today:
                try:
                    ann_this_year = dj.replace(year=today.year + 1)
                    years = today.year + 1 - dj.year
                except ValueError:
                    ann_this_year = dj.replace(year=today.year + 1, day=28)
                    years = today.year + 1 - dj.year
            else:
                years = today.year - dj.year
            delta = (ann_this_year - today).days
            if 0 <= delta <= days:
                upcoming.append({'employee': emp, 'days_until': delta, 'date': ann_this_year, 'years': years})
    return sorted(upcoming, key=lambda x: x['days_until'])


@login_required
def dashboard(request):
    # If employee role → redirect to their portal
    if get_user_role(request.user) == 'employee':
        return redirect('employee_portal')

    today = datetime.date.today()

    # Import core models safely
    try:
        from core.models import Announcement
        active_announcements = Announcement.objects.filter(is_active=True)[:10]
    except Exception:
        active_announcements = []

    context = {
        'total_employees': Employee.objects.filter(status='active').count(),
        'present_today': Attendance.objects.filter(date=today, status='present').count(),
        'pending_leaves': LeaveRequest.objects.filter(status='pending').count(),
        'paid_this_month': Payroll.objects.filter(
            month=today.month, year=today.year, status='paid'
        ).count(),
        'recent_employees': Employee.objects.order_by('-id')[:5],
        'recent_leaves': LeaveRequest.objects.select_related('employee', 'leave_type').order_by('-applied_on')[:5],
        'upcoming_birthdays': _get_upcoming_birthdays(30),
        'upcoming_anniversaries': _get_upcoming_anniversaries(30),
        'active_announcements': active_announcements,
    }
    return render(request, 'dashboard.html', context)
