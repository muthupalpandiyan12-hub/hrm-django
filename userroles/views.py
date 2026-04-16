from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone as dj_tz
from employees.models import Employee, Department
from attendance.models import Attendance
from leave.models import LeaveRequest, LeaveType
from leave.views import get_leave_balances
from payroll.models import Payroll
from punch.models import WorkSession
from .models import UserProfile
from .helpers import get_user_role, get_user_employee, admin_required
import datetime
import calendar as cal_module


def _get_portal_employee(request):
    """Helper to get employee or redirect."""
    return get_user_employee(request.user)


# ─────────────────────────────────────────
# HELPER: Derive status from total worked minutes
# ─────────────────────────────────────────
def _status_from_minutes(total_min):
    """
    ≥ 480 min (8 h)  → present
    ≥   1 min        → half_day
         0           → None (no record)
    """
    if total_min >= 480:
        return 'present'
    elif total_min >= 1:
        return 'half_day'
    return None


# ─────────────────────────────────────────
# HELPER: Build calendar grid for a month
# Uses WorkSession (punch) data as source of truth;
# falls back to Attendance records when no punch data exists.
# ─────────────────────────────────────────
def build_attendance_calendar(employee, month, year):
    """
    Returns a list of weeks; each week is 7 items (None = empty cell, or a dict).
    dict keys: day, date, status, check_in, check_out, total_minutes,
               total_display, is_today, is_future, is_weekend, has_record
    """
    # Manual attendance records (HR / admin entries)
    attendances = Attendance.objects.filter(
        employee=employee, date__month=month, date__year=year
    )
    att_map = {a.date.day: a for a in attendances}

    # Actual punch records for the month
    sessions = WorkSession.objects.filter(
        employee=employee, date__month=month, date__year=year
    ).order_by('punch_in')
    session_map = {}           # {day_int: [WorkSession, ...]}
    for s in sessions:
        session_map.setdefault(s.date.day, []).append(s)

    today = datetime.date.today()

    weeks = []
    for week in cal_module.monthcalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(None)
                continue
            current     = datetime.date(year, month, day)
            att         = att_map.get(day)
            day_sessions = session_map.get(day, [])

            if day_sessions:
                # ── WorkSession data is the ground truth ──
                total_min = sum(s.duration_minutes() for s in day_sessions)
                first_s   = min(day_sessions, key=lambda s: s.punch_in)
                last_s    = max(day_sessions, key=lambda s: s.punch_in)
                check_in  = dj_tz.localtime(first_s.punch_in).time()
                check_out = dj_tz.localtime(last_s.punch_out).time() if last_s.punch_out else None
                status    = _status_from_minutes(total_min)
                # Respect admin manual override for late/absent
                if att and att.status in ('late', 'absent'):
                    status = att.status
            elif att:
                # No punch data — use manual Attendance record
                total_min = 0
                check_in  = att.check_in
                check_out = att.check_out
                status    = att.status
            else:
                total_min = 0
                check_in  = None
                check_out = None
                status    = None

            total_display = (
                f"{total_min // 60}h {total_min % 60:02d}m" if total_min else '—'
            )

            row.append({
                'day'          : day,
                'date'         : current,
                'status'       : status,
                'check_in'     : check_in,
                'check_out'    : check_out,
                'total_minutes': total_min,
                'total_display': total_display,
                'is_today'     : current == today,
                'is_future'    : current > today,
                'is_weekend'   : current.weekday() >= 5,
                'has_record'   : att is not None or bool(day_sessions),
            })
        weeks.append(row)
    return weeks


# ─────────────────────────────────────────
# EMPLOYEE PORTAL
# ─────────────────────────────────────────

@login_required
def employee_portal(request):
    """Employee home — shows their own summary"""
    if get_user_role(request.user) == 'admin':
        return redirect('dashboard')

    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'No employee profile linked to your account. Contact HR.')
        return render(request, 'portal/no_profile.html')

    today = datetime.date.today()

    # Fetch active announcements
    try:
        from core.models import Announcement, Holiday
        active_announcements = Announcement.objects.filter(is_active=True)[:8]
        upcoming_holidays = [
            h for h in Holiday.objects.all()
            if h.date >= today and (h.date - today).days <= 30
        ]
    except Exception:
        active_announcements = []
        upcoming_holidays = []

    context = {
        'employee': employee,
        'today_attendance': Attendance.objects.filter(employee=employee, date=today).first(),
        'pending_leaves': LeaveRequest.objects.filter(employee=employee, status='pending').count(),
        'approved_leaves': LeaveRequest.objects.filter(employee=employee, status='approved').count(),
        'total_present': Attendance.objects.filter(employee=employee, status='present').count(),
        'recent_attendance': Attendance.objects.filter(employee=employee).order_by('-date')[:5],
        'recent_leaves': LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')[:3],
        'latest_payslip': Payroll.objects.filter(employee=employee).first(),
        'active_announcements': active_announcements,
        'upcoming_holidays': upcoming_holidays,
    }
    return render(request, 'portal/dashboard.html', context)


@login_required
def portal_attendance(request):
    """Employee views only their own attendance"""
    if get_user_role(request.user) == 'admin':
        return redirect('attendance_list')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    today = datetime.date.today()
    month = int(request.GET.get('month', today.month))
    year  = int(request.GET.get('year',  today.year))

    # ── Manual attendance records ──────────────────────────
    attendances = Attendance.objects.filter(
        employee=employee, date__month=month, date__year=year
    ).order_by('date')
    att_map = {a.date: a for a in attendances}

    # ── WorkSession records (actual punch data) ────────────
    all_sessions = WorkSession.objects.filter(
        employee=employee, date__month=month, date__year=year
    ).order_by('date', 'punch_in')

    session_by_date = {}          # {date: [WorkSession, ...]}
    for s in all_sessions:
        session_by_date.setdefault(s.date, []).append(s)

    # ── Build merged daily records (punch takes precedence) ─
    daily_records = []
    seen_dates    = set()

    for date_key, sessions in sorted(session_by_date.items()):
        seen_dates.add(date_key)
        total_min = sum(s.duration_minutes() for s in sessions)
        first_s   = min(sessions, key=lambda s: s.punch_in)
        last_s    = max(sessions, key=lambda s: s.punch_in)
        check_in  = dj_tz.localtime(first_s.punch_in).time()
        check_out = dj_tz.localtime(last_s.punch_out).time() if last_s.punch_out else None
        status    = _status_from_minutes(total_min) or 'absent'

        att = att_map.get(date_key)
        if att and att.status in ('late', 'absent'):
            status = att.status
        status_display_map = {
            'present': 'Present', 'absent': 'Absent',
            'half_day': 'Half Day', 'late': 'Late',
        }
        daily_records.append({
            'date'          : date_key,
            'status'        : status,
            'status_display': status_display_map.get(status, status.title()),
            'check_in'      : check_in,
            'check_out'     : check_out,
            'total_minutes' : total_min,
            'total_display' : (f"{total_min // 60}h {total_min % 60:02d}m" if total_min else '—'),
            'sessions_count': len(sessions),
            'note'          : (att.note if att else '') or '',
        })

    # Also include manual Attendance records with no punch data
    for att in attendances:
        if att.date not in seen_dates:
            daily_records.append({
                'date'          : att.date,
                'status'        : att.status,
                'status_display': att.get_status_display(),
                'check_in'      : att.check_in,
                'check_out'     : att.check_out,
                'total_minutes' : 0,
                'total_display' : '—',
                'sessions_count': 0,
                'note'          : att.note or '',
            })

    daily_records.sort(key=lambda r: r['date'], reverse=True)

    # ── Stats from merged records ──────────────────────────
    present  = sum(1 for r in daily_records if r['status'] == 'present')
    absent   = sum(1 for r in daily_records if r['status'] == 'absent')
    late     = sum(1 for r in daily_records if r['status'] == 'late')
    half_day = sum(1 for r in daily_records if r['status'] == 'half_day')

    # Prev / Next month for navigation links
    prev_date = datetime.date(year, month, 1) - datetime.timedelta(days=1)
    next_date = datetime.date(year, month, 1) + datetime.timedelta(days=32)
    next_date = next_date.replace(day=1)

    month_name = cal_module.month_name[month]

    context = {
        'employee'      : employee,
        'daily_records' : daily_records,
        'month'         : month,
        'year'          : year,
        'month_name'    : month_name,
        'months'        : range(1, 13),
        'years'         : range(today.year - 2, today.year + 1),
        'present'       : present,
        'absent'        : absent,
        'late'          : late,
        'half_day'      : half_day,
        'calendar_weeks': build_attendance_calendar(employee, month, year),
        'prev_month'    : prev_date.month,
        'prev_year'     : prev_date.year,
        'next_month'    : next_date.month,
        'next_year'     : next_date.year,
        'is_current'    : (month == today.month and year == today.year),
    }
    return render(request, 'portal/attendance.html', context)


@login_required
def portal_leaves(request):
    """Employee views and applies their own leaves"""
    if get_user_role(request.user) == 'admin':
        return redirect('leave_list')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    if request.method == 'POST':
        try:
            LeaveRequest.objects.create(
                employee=employee,
                leave_type_id=request.POST['leave_type'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                reason=request.POST['reason'],
            )
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('portal_leaves')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    leaves      = LeaveRequest.objects.filter(employee=employee).order_by('-applied_on')
    leave_types = LeaveType.objects.all()
    context = {
        'employee': employee,
        'leaves': leaves,
        'leave_types': leave_types,
        'pending':  leaves.filter(status='pending').count(),
        'approved': leaves.filter(status='approved').count(),
        'rejected': leaves.filter(status='rejected').count(),
        'balances': get_leave_balances(employee),
    }
    return render(request, 'portal/leaves.html', context)


@login_required
def portal_payslips(request):
    """Employee views only their own payslips"""
    if get_user_role(request.user) == 'admin':
        return redirect('payroll_list')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    payslips = Payroll.objects.filter(employee=employee).order_by('-year', '-month')
    context = {
        'employee': employee,
        'payslips': payslips,
        'total_paid': sum(p.net_salary for p in payslips if p.status == 'paid'),
    }
    return render(request, 'portal/payslips.html', context)


@login_required
def portal_profile(request):
    """Employee views their own profile"""
    if get_user_role(request.user) == 'admin':
        return redirect('dashboard')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    return render(request, 'portal/profile.html', {'employee': employee})


@login_required
def portal_reviews(request):
    """Employee sees their own performance reviews"""
    if get_user_role(request.user) == 'admin':
        return redirect('review_list')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    from performance.models import PerformanceReview
    reviews = PerformanceReview.objects.filter(employee=employee).order_by('-year', '-created_at')
    return render(request, 'portal/reviews.html', {'employee': employee, 'reviews': reviews})


# ─────────────────────────────────────────
# ADMIN — USER MANAGEMENT
# ─────────────────────────────────────────

@login_required
@admin_required
def user_list(request):
    """Admin sees all user accounts"""
    users = UserProfile.objects.select_related('user', 'employee').all()
    return render(request, 'userroles/user_list.html', {'users': users})


@login_required
@admin_required
def user_create(request):
    """Admin creates a login account for an employee"""
    employees   = Employee.objects.filter(status='active')
    departments = Department.objects.all()

    if request.method == 'POST':
        username   = request.POST.get('username')
        password   = request.POST.get('password')
        role       = request.POST.get('role', 'employee')
        emp_id     = request.POST.get('employee')
        dept_id    = request.POST.get('department')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
        else:
            user = User.objects.create_user(username=username, password=password)
            UserProfile.objects.create(
                user=user,
                role=role,
                employee_id=emp_id or None,
                department_id=dept_id or None,
            )
            messages.success(request, f'User "{username}" created successfully.')
            return redirect('user_list')

    return render(request, 'userroles/user_create.html', {
        'employees': employees,
        'departments': departments,
    })


@login_required
@admin_required
def user_delete(request, pk):
    """Admin deletes a user account"""
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        profile.user.delete()
        messages.success(request, 'User account deleted.')
        return redirect('user_list')
    return render(request, 'userroles/user_confirm_delete.html', {'profile': profile})
