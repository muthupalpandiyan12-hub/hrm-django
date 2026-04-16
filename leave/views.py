from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from employees.models import Employee
from .models import LeaveRequest, LeaveType


def get_leave_balances(employee):
    """Calculate leave balance for each leave type for an employee"""
    balances = []
    for lt in LeaveType.objects.all():
        used = LeaveRequest.objects.filter(
            employee=employee,
            leave_type=lt,
            status='approved'
        )
        used_days = sum(r.total_days() for r in used)
        remaining = lt.max_days - used_days
        balances.append({
            'leave_type': lt,
            'total':     lt.max_days,
            'used':      used_days,
            'remaining': max(remaining, 0),
            'percent':   min(int((used_days / lt.max_days) * 100), 100) if lt.max_days > 0 else 0,
        })
    return balances


@login_required
def leave_list(request):
    leaves        = LeaveRequest.objects.select_related('employee', 'leave_type').all()
    status_filter = request.GET.get('status', '')
    emp_filter    = request.GET.get('employee', '')

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if emp_filter:
        leaves = leaves.filter(employee_id=emp_filter)

    employees   = Employee.objects.filter(status='active')
    leave_types = LeaveType.objects.all()

    # Overall balance summary for all employees
    all_balances = []
    for emp in employees:
        all_balances.append({
            'employee':  emp,
            'balances': get_leave_balances(emp),
        })

    return render(request, 'leave/list.html', {
        'leaves':        leaves,
        'status_filter': status_filter,
        'emp_filter':    emp_filter,
        'employees':     employees,
        'leave_types':   leave_types,
        'all_balances':  all_balances,
    })


@login_required
def leave_apply(request):
    employees   = Employee.objects.filter(status='active')
    leave_types = LeaveType.objects.all()
    if request.method == 'POST':
        try:
            LeaveRequest.objects.create(
                employee_id=request.POST['employee'],
                leave_type_id=request.POST['leave_type'],
                start_date=request.POST['start_date'],
                end_date=request.POST['end_date'],
                reason=request.POST['reason'],
            )
            messages.success(request, 'Leave request submitted.')
            return redirect('leave_list')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'leave/apply.html', {'employees': employees, 'leave_types': leave_types})


@login_required
def leave_approve(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        leave.status   = 'approved' if action == 'approve' else 'rejected'
        leave.remarks  = request.POST.get('remarks', '')
        leave.reviewed_on = timezone.now()
        leave.save()
        messages.success(request, f'Leave request {leave.status}.')
        return redirect('leave_list')
    return render(request, 'leave/approve.html', {'leave': leave})


@login_required
def leave_delete(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Leave request deleted.')
        return redirect('leave_list')
    return render(request, 'leave/confirm_delete.html', {'leave': leave})


@login_required
def leave_balance(request):
    """Admin views leave balance for all employees"""
    employees   = Employee.objects.filter(status='active')
    emp_filter  = request.GET.get('employee', '')
    if emp_filter:
        employees = employees.filter(pk=emp_filter)

    all_balances = []
    for emp in employees:
        all_balances.append({
            'employee': emp,
            'balances': get_leave_balances(emp),
        })

    return render(request, 'leave/balance.html', {
        'all_balances':   all_balances,
        'employees_list': Employee.objects.filter(status='active'),
        'emp_filter':     emp_filter,
    })
