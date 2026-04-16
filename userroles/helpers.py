from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def get_user_role(user):
    """Returns role: 'admin' or 'employee'"""
    try:
        return user.profile.role
    except Exception:
        return 'admin' if user.is_superuser else 'employee'


def get_user_employee(user):
    """Returns linked Employee object or None"""
    try:
        return user.profile.employee
    except Exception:
        return None


def admin_required(view_func):
    """Only admin can access this view"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if get_user_role(request.user) != 'admin':
            messages.error(request, 'Access denied. Admins only.')
            return redirect('employee_portal')
        return view_func(request, *args, **kwargs)
    return wrapper
