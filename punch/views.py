from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from employees.models import Employee
from .models import WorkSession
from userroles.helpers import get_user_role, get_user_employee, admin_required
import datetime


# ─────────────────────────────────────────────────────────
# HELPER: Build full daily summary for one employee & date
# ─────────────────────────────────────────────────────────
def get_daily_summary(employee, date):
    sessions = list(
        WorkSession.objects.filter(employee=employee, date=date).order_by('punch_in')
    )
    total_minutes = sum(s.duration_minutes() for s in sessions)

    # Breaks = gaps between consecutive sessions
    breaks = []
    for i in range(len(sessions) - 1):
        prev = sessions[i]
        curr = sessions[i + 1]
        if prev.punch_out:
            break_start = prev.punch_out
            break_end   = curr.punch_in
            break_mins  = max(0, int((break_end - break_start).total_seconds() / 60))
            breaks.append({
                'number'  : i + 1,
                'start'   : timezone.localtime(break_start),
                'end'     : timezone.localtime(break_end),
                'minutes' : break_mins,
                'display' : f"{break_mins // 60}h {break_mins % 60:02d}m" if break_mins >= 60
                            else f"{break_mins}m",
            })

    TARGET = 480          # 8 hours in minutes
    remaining = max(0, TARGET - total_minutes)
    percent   = min(100, int((total_minutes / TARGET) * 100)) if TARGET else 0

    active_session = next((s for s in sessions if s.is_active), None)

    return {
        'sessions'            : sessions,
        'total_minutes'       : total_minutes,
        'total_display'       : f"{total_minutes // 60}h {total_minutes % 60:02d}m",
        'breaks'              : breaks,
        'break_count'         : len(breaks),
        'total_break_minutes' : sum(b['minutes'] for b in breaks),
        'total_break_display' : (lambda m: f"{m // 60}h {m % 60:02d}m" if m >= 60 else f"{m}m")(sum(b['minutes'] for b in breaks)),
        'target_minutes'      : TARGET,
        'remaining_minutes'   : remaining,
        'remaining_display'   : f"{remaining // 60}h {remaining % 60:02d}m",
        'percent'             : percent,
        'is_complete'         : total_minutes >= TARGET,
        'is_active'           : active_session is not None,
        'active_session'      : active_session,
        'first_punch_in'      : timezone.localtime(sessions[0].punch_in)  if sessions else None,
        'last_punch_out'      : timezone.localtime(sessions[-1].punch_out) if sessions and sessions[-1].punch_out else None,
    }


# ─────────────────────────────────────────────────────────
# EMPLOYEE PUNCH DASHBOARD
# ─────────────────────────────────────────────────────────
@login_required
def punch_dashboard(request):
    if get_user_role(request.user) == 'admin':
        return redirect('punch_admin')

    employee = get_user_employee(request.user)
    if not employee:
        messages.error(request, 'No employee profile linked. Contact HR.')
        return redirect('employee_portal')

    today   = datetime.date.today()
    summary = get_daily_summary(employee, today)

    # Last 7 days history (skip today)
    history = []
    for i in range(1, 8):
        d = today - datetime.timedelta(days=i)
        s = get_daily_summary(employee, d)
        history.append({'date': d, **s})

    return render(request, 'punch/dashboard.html', {
        'employee': employee,
        'today'   : today,
        'summary' : summary,
        'history' : history,
    })


# ─────────────────────────────────────────────────────────
# PUNCH IN
# ─────────────────────────────────────────────────────────
@login_required
def punch_in(request):
    if request.method != 'POST':
        return redirect('punch_dashboard')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    today = datetime.date.today()

    # Block double punch-in
    if WorkSession.objects.filter(employee=employee, date=today, punch_out__isnull=True).exists():
        messages.warning(request, '⚠️ You are already punched in. Please punch out first.')
        return redirect('punch_dashboard')

    now = timezone.now()
    WorkSession.objects.create(employee=employee, date=today, punch_in=now)
    messages.success(request, f'✅ Punched IN at {timezone.localtime(now).strftime("%I:%M %p")}')
    return redirect('punch_dashboard')


# ─────────────────────────────────────────────────────────
# PUNCH OUT
# ─────────────────────────────────────────────────────────
@login_required
def punch_out(request):
    if request.method != 'POST':
        return redirect('punch_dashboard')

    employee = get_user_employee(request.user)
    if not employee:
        return redirect('employee_portal')

    today = datetime.date.today()
    active = WorkSession.objects.filter(
        employee=employee, date=today, punch_out__isnull=True
    ).first()

    if not active:
        messages.warning(request, '⚠️ No active session. Please punch in first.')
        return redirect('punch_dashboard')

    now = timezone.now()
    active.punch_out = now
    active.save()
    dur = active.duration_display()
    messages.success(
        request,
        f'✅ Punched OUT at {timezone.localtime(now).strftime("%I:%M %p")} — Session: {dur}'
    )
    return redirect('punch_dashboard')


# ─────────────────────────────────────────────────────────
# ADMIN — ALL EMPLOYEES PUNCH RECORDS
# ─────────────────────────────────────────────────────────
@login_required
@admin_required
def punch_admin(request):
    date_str = request.GET.get('date', str(datetime.date.today()))
    try:
        selected_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        selected_date = datetime.date.today()

    employees = Employee.objects.filter(status='active').order_by('name')

    all_summaries = []
    for emp in employees:
        s = get_daily_summary(emp, selected_date)
        all_summaries.append({'employee': emp, **s})

    # Sort: currently active first → then by total minutes desc → absent last
    all_summaries.sort(key=lambda x: (
        0 if x['is_active'] else (1 if x['sessions'] else 2),
        -x['total_minutes']
    ))

    unclosed_count = WorkSession.objects.filter(punch_out__isnull=True).count()

    return render(request, 'punch/admin_list.html', {
        'selected_date' : selected_date,
        'all_summaries' : all_summaries,
        'present_count' : sum(1 for s in all_summaries if s['sessions']),
        'active_count'  : sum(1 for s in all_summaries if s['is_active']),
        'complete_count': sum(1 for s in all_summaries if s['is_complete']),
        'absent_count'  : sum(1 for s in all_summaries if not s['sessions']),
        'unclosed_count': unclosed_count,
    })


# ─────────────────────────────────────────────────────────
# ADMIN — VIEW ONE EMPLOYEE'S FULL PUNCH DETAIL
# ─────────────────────────────────────────────────────────
@login_required
@admin_required
def punch_employee_detail(request, emp_id):
    employee = get_object_or_404(Employee, pk=emp_id)

    date_str = request.GET.get('date', str(datetime.date.today()))
    try:
        selected_date = datetime.date.fromisoformat(date_str)
    except ValueError:
        selected_date = datetime.date.today()

    today = datetime.date.today()
    summary = get_daily_summary(employee, selected_date)

    # Last 7 days history
    history = []
    for i in range(1, 8):
        d = selected_date - datetime.timedelta(days=i)
        s = get_daily_summary(employee, d)
        history.append({'date': d, **s})

    return render(request, 'punch/employee_detail.html', {
        'employee'      : employee,
        'selected_date' : selected_date,
        'today'         : today,
        'summary'       : summary,
        'history'       : history,
    })


# ─────────────────────────────────────────────────────────
# ADMIN — FORCE CLOSE AN OPEN SESSION
# ─────────────────────────────────────────────────────────
@login_required
@admin_required
def force_close_session(request, session_id):
    session = get_object_or_404(WorkSession, pk=session_id)

    if request.method == 'POST':
        close_time_str = request.POST.get('close_time', '')
        if close_time_str:
            try:
                # Parse the datetime-local input (format: YYYY-MM-DDTHH:MM)
                import pytz
                naive_dt = datetime.datetime.fromisoformat(close_time_str)
                ist = pytz.timezone('Asia/Kolkata')
                aware_dt = ist.localize(naive_dt)
                # Ensure it's after punch_in
                if aware_dt <= session.punch_in:
                    messages.error(request, 'Close time must be after punch-in time.')
                else:
                    session.punch_out = aware_dt
                    session.save()
                    messages.success(request, f'Session closed at {aware_dt.strftime("%d %b %Y, %I:%M %p")}.')
            except Exception as e:
                messages.error(request, f'Error: {e}')
        else:
            # Close at punch_in + 8 hours if no time given
            session.punch_out = session.punch_in + datetime.timedelta(hours=8)
            session.save()
            messages.success(request, 'Session auto-closed at 8 hours from punch-in.')

        return redirect('punch_employee_detail', emp_id=session.employee_id)

    # GET — show confirmation page (shouldn't happen but handle gracefully)
    return redirect('punch_employee_detail', emp_id=session.employee_id)


# ─────────────────────────────────────────────────────────
# ADMIN — LIST ALL UNCLOSED SESSIONS ACROSS ALL EMPLOYEES
# ─────────────────────────────────────────────────────────
@login_required
@admin_required
def unclosed_sessions(request):
    open_sessions = WorkSession.objects.filter(
        punch_out__isnull=True
    ).select_related('employee').order_by('punch_in')

    # Annotate with hours running
    now = timezone.now()
    session_data = []
    for s in open_sessions:
        running_minutes = int((now - s.punch_in).total_seconds() / 60)
        session_data.append({
            'session'         : s,
            'running_display' : f"{running_minutes // 60}h {running_minutes % 60:02d}m",
            'running_minutes' : running_minutes,
            'is_long'         : running_minutes > 600,   # >10 hours = problem
            'punch_in_local'  : timezone.localtime(s.punch_in),
        })

    return render(request, 'punch/unclosed_sessions.html', {
        'session_data': session_data,
        'total'       : len(session_data),
    })
