from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Avg
import datetime
import json
from .models import Holiday, Announcement
from userroles.helpers import admin_required


@admin_required
def holiday_list(request):
    if request.method == 'POST':
        try:
            Holiday.objects.create(
                name=request.POST['name'],
                date=request.POST['date'],
                holiday_type=request.POST.get('holiday_type', 'public'),
                description=request.POST.get('description', ''),
            )
            messages.success(request, 'Holiday added successfully.')
            return redirect('holiday_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    today = datetime.date.today()
    holidays = Holiday.objects.all()
    # Annotate days until each holiday
    holiday_data = []
    for h in holidays:
        if h.date >= today:
            days_until = (h.date - today).days
        else:
            days_until = None
        holiday_data.append({'holiday': h, 'days_until': days_until})

    return render(request, 'core/holiday_list.html', {
        'holiday_data': holiday_data,
        'type_choices': Holiday.TYPE_CHOICES,
    })


@admin_required
def holiday_delete(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, 'Holiday deleted.')
        return redirect('holiday_list')
    return redirect('holiday_list')


@admin_required
def announcement_list(request):
    if request.method == 'POST':
        try:
            Announcement.objects.create(
                title=request.POST['title'],
                content=request.POST['content'],
                priority=request.POST.get('priority', 'medium'),
                is_active=request.POST.get('is_active') == 'on',
                expires_on=request.POST.get('expires_on') or None,
                posted_by=request.user,
            )
            messages.success(request, 'Announcement posted successfully.')
            return redirect('announcement_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    announcements = Announcement.objects.all()
    return render(request, 'core/announcement_list.html', {
        'announcements': announcements,
        'priority_choices': Announcement.PRIORITY_CHOICES,
    })


@admin_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted.')
        return redirect('announcement_list')
    return redirect('announcement_list')


@admin_required
def reports(request):
    from attendance.models import Attendance
    from employees.models import Employee, Department
    from performance.models import PerformanceReview

    today = datetime.date.today()
    current_year = today.year

    # ── 1. Monthly Attendance Report (current year) ──────────────────────────
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    present_counts = [0] * 12
    absent_counts  = [0] * 12
    late_counts    = [0] * 12
    half_day_counts= [0] * 12

    attendance_qs = (
        Attendance.objects
        .filter(date__year=current_year)
        .values('date__month', 'status')
        .annotate(total=Count('id'))
    )
    for row in attendance_qs:
        m = row['date__month'] - 1   # 0-indexed
        s = row['status']
        if s == 'present':
            present_counts[m] = row['total']
        elif s == 'absent':
            absent_counts[m] = row['total']
        elif s == 'late':
            late_counts[m] = row['total']
        elif s == 'half_day':
            half_day_counts[m] = row['total']

    # ── 2. Department-wise Salary Report ─────────────────────────────────────
    dept_salary_qs = (
        Employee.objects
        .filter(status='active', department__isnull=False)
        .values('department__name')
        .annotate(total_salary=Sum('salary'), headcount=Count('id'))
        .order_by('-total_salary')
    )
    dept_labels   = [r['department__name'] for r in dept_salary_qs]
    dept_salaries = [float(r['total_salary']) for r in dept_salary_qs]
    dept_counts   = [r['headcount'] for r in dept_salary_qs]

    # ── 3. Employee Performance Chart (avg rating per employee, top 10) ──────
    perf_qs = (
        PerformanceReview.objects
        .values('employee__name')
        .annotate(avg_rating=Avg('rating'))
        .order_by('-avg_rating')[:10]
    )
    perf_labels  = [r['employee__name'] for r in perf_qs]
    perf_ratings = [round(float(r['avg_rating']), 2) for r in perf_qs]

    # ── Summary numbers ───────────────────────────────────────────────────────
    total_employees   = Employee.objects.filter(status='active').count()
    total_departments = Department.objects.count()
    this_month_present = Attendance.objects.filter(
        date__year=today.year, date__month=today.month, status='present'
    ).count()
    avg_salary = Employee.objects.filter(status='active').aggregate(
        avg=Avg('salary'))['avg'] or 0

    context = {
        'current_year': current_year,
        'month_names':  json.dumps(month_names),
        'present_counts':  json.dumps(present_counts),
        'absent_counts':   json.dumps(absent_counts),
        'late_counts':     json.dumps(late_counts),
        'half_day_counts': json.dumps(half_day_counts),
        'dept_labels':    json.dumps(dept_labels),
        'dept_salaries':  json.dumps(dept_salaries),
        'dept_counts':    dept_counts,
        'perf_labels':    json.dumps(perf_labels),
        'perf_ratings':   json.dumps(perf_ratings),
        # summary cards
        'total_employees':   total_employees,
        'total_departments': total_departments,
        'this_month_present': this_month_present,
        'avg_salary': round(avg_salary, 2),
    }
    return render(request, 'core/reports.html', context)
